import streamlit as st
import requests
import json
import logging
import time
import streamlit as st
import re
import pandas as pd 
from pandas import  ExcelWriter
from io import BytesIO
from datetime import date
import numpy as np
import os
from os import getcwd
from datetime import timedelta

import collections
import secrets

class Instructions:
    instructions = 'Enter the depot name, Paste in schedule 1 and schedule 2, check the domain is supported by the api call, run the script'
    link = '#'

class Description:
    title = "Schedule Comparison"
    description = "This is a script that uses the Optibus API amd compares schedules from optibus urls to create an excel file, highlighting the savings between scenarios"
    icon = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmaLtoRAJT4nxBOCBs_mQapmWJv3gxDjaYIQ&usqp=CAU"
    author = 'Luke Norman'

def run():
    
    #TODO: may need other client names - only have partial set so far 
    clients_dict = {
        'arriva-uk-bus': 'Arriva UK', 
        'sg': 'Stagecoach', 
        'firstbus': 'First Bus',
        'drrichard':'Dr Richard'
    }

    #Info
    st.caption('*Author: Luke Norman*')
    support = st.expander('Supported Clients')
    support.write('Stagecoach, Arriva, First Bus, Dr Richard')
    support.caption('Please Contact the author if you wish a client to be supported for this api comparison')
    

    #TODO: Save this to a secrets.toml file 
    api_secrets_dict= st.secrets['api_secrets_dict']

    #Stat property list
    stat_properties = ["crew_schedule_stats.paid_time", 
    "crew_schedule_stats.attendance_time", 
    "crew_schedule_stats.custom_time_definitions", 
    "crew_schedule_stats.depot_pull_time", 
    "crew_schedule_stats.duties_count", 
    "crew_schedule_stats.histograms", 
    "crew_schedule_stats.length", 
    "crew_schedule_stats.sign_off_time", 
    "crew_schedule_stats.sign_on_time", 
    "crew_schedule_stats.split_count", 
    "vehicle_schedule_stats.depot_allocations", 
    "vehicle_schedule_stats.driving_time", 
    "vehicle_schedule_stats.platform_time", 
    "vehicle_schedule_stats.pvr", 
    "crew_schedule_stats.changeover_count", 
    "crew_schedule_stats.standby_time", 
    "crew_schedule_stats.algorithmic_cost", 
    "crew_schedule_stats.custom_time_definitions", 
    "crew_schedule_stats.unscheduled_duty_count", 
    "relief_vehicle_schedule_stats.relief_vehicle_count"]

    #function to split URL into three substrings
    def process_URL(schedule_URL):
        domain_name = re.sub("\.[^.]*", "", schedule_URL[8:])
        schedule_id = schedule_URL
        schedule_id = re.sub(r'^.*?(?=schedules/)', "", schedule_id)
        schedule_id = schedule_id[10:].split('/', -1)[0]
        project_id = schedule_URL
        project_id = re.sub(r'^.*?(?=project/)', "", project_id)
        project_id = project_id[8:].split('/', -1)[0]
        return domain_name, schedule_id , project_id

    #Function to get client_id and secret based on the domain name key pasted in the URL
    def generate_auth(domain_name, api_secrets_dict):
        client_id = api_secrets_dict[domain_name]["client_id"]
        client_secret = api_secrets_dict[domain_name]["client_secret"]
        return client_id, client_secret

    #Function to use auth server endoiunt to get new token 
    def get_new_token(client_id, client_secret, domain_name, a):
        auth_server_url = f"https://{domain_name}.optibus.co/api/v2/token"
        token_req_payload = {'grant_type': 'client_credentials'}
        if domain_name != "":
            token_response = requests.post(auth_server_url,
            data=token_req_payload, verify=False, allow_redirects=False,
            auth=(client_id, client_secret))          
            if token_response.status_code !=200:
                col1, col2 = st.columns([8,2])
                with col1:
                    st.error(f"Failed to obtain token from the OAuth 2.0 server **{token_response.status_code}**")
                with col2:
                    rerun = st.button('Retry')
                    if rerun: 
                        st.experimental_rerun()
                    else:
                        st.stop()
            else:
                #st.success(f"Successfuly obtained a new token for **{a} Schedule**")
                tokens = json.loads(token_response.text)
                return tokens['access_token']
        else:
            st.stop()

    # Variable for download button
    download_run_arriva = ''
    download_run_optibus = ''

    def get_optibus_id(token, domain_name, schedule_id):
        api_call_headers = {'Authorization': 'Bearer ' + token}
        api_call_response = requests.get(f'https://{domain_name}.optibus.co/api/v2/schedules/meta?scheduleIds[]={schedule_id}&includeHidden=true&includeDeleted=true', headers=api_call_headers, verify=False)
        get_json = api_call_response.json()
        for d in get_json:
            optibus_id = d['schedule']['optibusId']
            dataset_id = d['dataset']['optibusId']
        return optibus_id, dataset_id


    def api_meta_response(token, domain_name, schedule_id, stat_properties):
        api_call_headers = {'Authorization': 'Bearer ' + token}

        #Initial call without parameters
        api_call = f'https://{domain_name}.optibus.co/api/v2/schedules/meta?scheduleIds[]={schedule_id}&includeHidden=true&includeDeleted=true'

        #Iterate and append parameters to the stat_property component of api string
        for property in stat_properties:
            api_call += f'&statProperties[]={property}'

        api_call_response = requests.get(api_call, headers=api_call_headers, verify=False)

        #OLD API STRING (QUITE DIFFICULT TO READ)
        #api_call_response = requests.get(f'https://{domain_name}.optibus.co/api/v2/schedules/meta?scheduleIds[]={schedule_id}&includeHidden=true&includeDeleted=true&statProperties[]=crew_schedule_stats.paid_time&statProperties[]=crew_schedule_stats.attendance_time&statProperties[]=crew_schedule_stats.custom_time_definitions&statProperties[]=crew_schedule_stats.depot_pull_time&statProperties[]=crew_schedule_stats.duties_count&statProperties[]=crew_schedule_stats.histograms&statProperties[]=crew_schedule_stats.length&statProperties[]=crew_schedule_stats.sign_off_time&statProperties[]=crew_schedule_stats.sign_on_time&statProperties[]=crew_schedule_stats.split_count&statProperties[]=vehicle_schedule_stats.depot_allocations&statProperties[]=vehicle_schedule_stats.driving_time&statProperties[]=vehicle_schedule_stats.platform_time&statProperties[]=vehicle_schedule_stats.pvr', headers=api_call_headers, verify=False)

        get_json = api_call_response.json()
        return get_json

    def create_json_list(get_services_json, token, domain_name, stat_properties):
        emp_list = []
        exclude = ['NWD', '#SCH', 'NSCH', german_secelct]
        for d in get_services_json:
            if not any(substring in d['name'] for substring in exclude):
                emp_list.append(api_meta_response(token, domain_name, d['id'], stat_properties))

        flattened_list = [item for sublist in emp_list for item in sublist]
        return flattened_list

    def catch_service_lists(json_data_list, key, key2):
        result = []
        for d in json_data_list:
            result.extend(d.get(key, {}).get(key2, []))
        return result

    #return individual values from json dict
    def get_duties(get_json):
        duty_count = get_json['stats']['crew_schedule_stats']['duties_count']
        return duty_count

    #return individual values from json dict
    def get_paid_time(get_json):
        paid_time = get_json['stats']['crew_schedule_stats']['paid_time']
        return paid_time

    #calculation of avg paid time
    def calculate_avg_paid_time(paid_time, duty_count):
        avg_paid_time = [paid_time[i]/duty_count[i] for i in range(len(paid_time))]
        return avg_paid_time

    #return individual values from json dict
    def get_platform_time(get_json):
        platform_time = get_json['stats']['vehicle_schedule_stats']['platform_time']
        return platform_time

    #Calculation of schedule efficiency (FUNCTION SHOULD REALLY BE CHANGED TO calculate_sch_eff)
    def get_sch_eff(platform_time, paid_time):
        efficiency = [(platform_time[i]/paid_time[i])*100 for i in range(len(platform_time))]
        return efficiency

    #Calculation of efficiency difference 
    def calculate_eff_diff(efficiency_ba, efficiency_op):
        eff_diff = [round(efficiency_op[i] - efficiency_ba[i], 2) for i in range(len(efficiency_op))]
        return eff_diff

    #Calculation of duty count difference
    def calculate_duty_diff(duty_count_ba, duty_count_op):
        duty_count_diff = int(duty_count_ba - duty_count_op)
        return duty_count_diff

    #Calculation of paid time difference 
    def calculate_paid_time_diff(paid_time_ba, paid_time_op):
        pt_diff = paid_time_ba - paid_time_op
        return pt_diff

    #Converting minutes into a HH:MM string time format
    def minutes_to_hours(minutes):
        # Calculate the number of hours
        hours = int(minutes // 60)
        # Calculate the number of remaining minutes
        remaining_minutes = int(minutes % 60)
        # Return the hours and minutes as a string, separated by a colon
        return f"{hours}:{remaining_minutes:02d}"

    #Function to concatenate the values of one list with the values of another and return two lists, project name and also the concatenated list
    def get_values(dict_list, key1, key2):
        return [d[key1] for d in dict_list], [d[key1] +' - '+ d[key2] for d in dict_list]

    #get index of where deleted row should be 
    def get_index(dict_list, key, value):
        for i, d in enumerate(dict_list):
            if d[key] == value:
                return i
        return -1



    def get_days_of_week(get_json):
        dow = get_json['service']['daysOfWeek']
        return dow



    def api_services_response(token, domain_name, optibus_id):
        api_call_headers = {'Authorization': 'Bearer ' + token}
        api_call_response = requests.get(f'https://{domain_name}.optibus.co/api/v2/schedule/{optibus_id}/services', headers=api_call_headers, verify=False)
        get_services_json = api_call_response.json()
        return get_services_json


    def return_assciated_Serv_days(check_serv, string):
        master_list = [2,3,4,5,6,7,1]
        master_dict =  service_days_dict={1:'Sun',2:'Mon',3:'Tue',4:'Wed',5:'Thur',6:'Fri',7:'Sat'}
        missing_elements = set(master_list) - set(check_serv)
        missing_days = [master_dict[x] for x in missing_elements] 
        return missing_days, string


    def create_schedule_names(get_json):
        name = get_json['scheduleSet']['id']
        return name

    def create_service_ids_list(json_data_list):
        list = []
        # Iterate through the list of dictionaries
        for sch_d in json_data_list:
            # Access the value of the 'list_key' key
            list_value = sch_d['service']['daysOfWeek']
            list.append(list_value)
        flat_list = []
        for sublist in list:
            for elements in sublist:
                flat_list.append(elements)

        return flat_list

    def create_paid_time_list(json_data_list):
        # List to store the results
        paid_time_list = []
        paid_time_result_list = []

        # Iterate through the list of dictionaries
        for sch_d in json_data_list:
            # Multiply the value of the 'other_key' key by the length of the list
            result = sch_d['service']['stats']['crew_schedule_stats']['paid_time'] 
            paid_time_result_list += [result] * len(sch_d['service']['daysOfWeek'])

            # Append the result to the result list
            paid_time_list.append(result)

        paid_time_list_sum = sum(paid_time_list)
        return paid_time_list, paid_time_list_sum, paid_time_result_list

    # Function to retrieve Paid Break time
    def create_paid_break_time_list(json_data_list):
        result = []
        for d in json_data_list:
            inner_list = []
            for l in d['service']['stats']['crew_schedule_stats']['custom_time_definitions']:
                if l['name']=='Paid Break':
                    inner_list.append(l['value'])
            result.append(sum(inner_list))
        return result

    def get_duty_types(json_data_list,service_days):
        duty_type_list = []
        for d in json_data_list:
            duty_type_list.append(d['service']['stats']['crew_schedule_stats']['histograms']['duty_types'])
            # duty_type_df = pd.DataFrame.from_records(duty_type_list)
        duty_type_dic = dict(zip(service_days,duty_type_list)) 
        #duty_type_df = pd.DataFrame.from_dict(duty_type_dic, orient= 'columns')
        # Find the maximum number of items in the lists
        max_length = max(len(v) for v in duty_type_dic.values())

        # Pad the lists with NaN values
        for key in duty_type_dic:
            duty_type_dic[key] += [float('nan')] * (max_length - len(duty_type_dic[key]))

        # Create DataFrame
        duty_type_df = pd.DataFrame(duty_type_dic)

        return duty_type_df

    def create_meta_time_list(json_data_list, mode, string):
        # List to store the results
        meta_time_list = []
        meta_time_result_list = []

        # Iterate through the list of dictionaries
        for sch_d in json_data_list:
            # Access the value of the 'list_key' key
            list_value = sch_d['service']['daysOfWeek']

            # Get the length of the list
            list_length = len(list_value)
            result = sch_d['service']['stats'][f'{mode}_schedule_stats'][string] 
            for i in range (list_length):
                meta_time_result_list.append(result)

            # Append the result to the result list
            meta_time_list.append(result)

        meta_time_list_sum = sum(meta_time_list)
        return meta_time_list, meta_time_list_sum, meta_time_result_list

    def create_meta_count_list(json_data_list, mode, string):
        # List to store the results
        meta_count_list = []
        meta_count_result_list = []

        # Iterate through the list of dictionaries
        for sch_d in json_data_list:
            # Access the value of the 'list_key' key
            list_value = sch_d['service']['daysOfWeek']

            # Get the length of the list
            list_length = len(list_value)
            try:
                # Multiply the value of the 'other_key' key by the length of the list
                result = sch_d['service']['stats'][f'{mode}_schedule_stats'][string]
                for i in range (list_length):
                    meta_count_result_list.append(result) 
            except:
                result = 0
                for i in range (list_length):
                    meta_count_result_list.append(result)                  

            # Append the result to the result list
            meta_count_list.append(result)

        meta_count_list_sum = sum(meta_count_list)
        return meta_count_list, meta_count_list_sum, meta_count_result_list

    def retrieve_service_groups(json_data_list):
        # List to store the results
        service_groups = []
        # Iterate through the list of dictionaries
        for sch_d in json_data_list:
            # Access the value of the 'list_key' key
            services= sch_d['service']['name']
            service_groups.append(services)  
        return service_groups
    def change_to_hours(df,string):
        df.loc[string] = df.loc[string].apply(lambda x: f"{int(x/60)}:{int(abs(x/60-int(x/60))*60):02d}")

    dow = None


    with st.form('API Request parameters'):

        #Project Name text input as can't pull it consistently from API - MUST not be blank - validation step later on on form submission
        depot_name = st.text_input('Name of Project', placeholder='Derby')
        #Text input for URL baseline 
        schedule_URL_baseline = st.text_input(label= 'Please type the baseline schedule URL here', placeholder='https://domain.optibus.co/project/t4bx3pnc0/schedules/oBAwkfaRv/gantt?type=duties')
        #Text input for URL optimisation 
        schedule_URL_optimisation = st.text_input(label= 'Please type the optimised schedule URL here', placeholder='https://domain.optibus.co/project/t4bx3pnc0/schedules/oBAwkfaRv/gantt?type=duties', key = 'b')

        #function to process URL into substring variables used for API 
        domain_name_ba, schedule_id_ba , project_id_ba = process_URL(schedule_URL_baseline)
        #//
        domain_name_op, schedule_id_op , project_id_op = process_URL(schedule_URL_optimisation)


        with st.expander('Options'):
            same_project_overide = st.checkbox('*Compare schedules from different projects*')
            time_formats = st.radio('*Reporting Time formats*', ['[h].d','minutes','[h]:mm'], horizontal=True)

        #Check if text input is not blank
        if schedule_URL_optimisation != '':
            #Get id and secret based on url that has been entered 
            client_id_baseline , client_secret_baseline= generate_auth(domain_name_ba, api_secrets_dict)
            #//
            client_id_optimisation, client_secret_optimisation= generate_auth(domain_name_op, api_secrets_dict)


        #Form submit button
        submit = st.form_submit_button('Submit', type='primary')
        #IF clicked
        if submit:
            #Check if project name is blank
            download_run_optibus = 'run'
            if not depot_name:
                #Info 
                st.warning("**Project Name** can't be left blank")

            #check that project id matches for baseline and optimisation URL 
            elif project_id_ba != project_id_op and same_project_overide == False:
                st.error('Please upload all comparisons from the **Same** project!')

            #if all other conditions are met - continue to call the API 
            else:
                #Present progress bar 
                my_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)
                my_bar.progress(100)



                token_baseline = get_new_token(client_id_baseline, client_secret_baseline, domain_name_ba, 'Baseline')
                token_optimisation = get_new_token(client_id_optimisation, client_secret_optimisation, domain_name_op, 'Optimisation')

                #get_json_test1 = api_header_response(token_baseline, domain_name_ba, schedule_id_ba)
                #st.write(get_json_test1)
                #Example to get the optibus ID from a schedule and then use servrices endpoint
                #.compensationtime

                optibus_id_ba, dataset_id_ba  = get_optibus_id(token_baseline, domain_name_ba, schedule_id_ba)
                optibus_id_op, dataset_id_op = get_optibus_id(token_optimisation, domain_name_op, schedule_id_op)



                if 'status' in optibus_id_ba and optibus_id_ba['status'] == 500:
                    url_check = 'Baseline URL'
                    st.warning(f'There is an issue with **{url_check}**, please *Save a new version of the schedule* and try again, this is a known API issue. Please see message below for further details')
                    st.caption(optibus_id_ba)
                    st.stop()
                elif 'status' in optibus_id_op and optibus_id_op['status'] == 500:
                    url_check = 'Optimisation URL'
                    st.warning(f'There is an issue with **{url_check}**, please *Save a new version of the schedule* and try again, this is a known API issue. Please see message below for further details')
                    st.caption(optibus_id_op)
                    st.stop()

                get_services_json_ba = api_services_response(token_baseline, domain_name_ba, optibus_id_ba)
                get_services_json_op = api_services_response(token_optimisation, domain_name_op, optibus_id_op)


                #&statProperties[]=crew_schedule_stats.paid_time&statProperties[]=general_stats&statProperties[]=relief_vehicle_schedule_stats&statProperties[]=relief_vehicle_schedule_stats
                #st.write(get_services_json_ba)
                #st.write(get_services_json_ba)



                if domain_name_ba == 'drrichard':
                    german_secelct = st.selectbox(label='Exclude', options= ['oS', 'mS'])
                else: 
                    german_secelct = 'UNKNOWN'



                json_data_list_ba = create_json_list(get_services_json_ba, token_baseline, domain_name_ba, stat_properties)
                json_data_list_op = create_json_list(get_services_json_op, token_optimisation, domain_name_op, stat_properties)




                for key in clients_dict:
                        # check if the key is a substring of the string
                        if key in domain_name_ba:
                            # if it is, assign a new variable the corresponding value
                            client_instance = clients_dict[key]

                    #call functions defined earlier on to get specific data from the API - CAN ALWAYS BE UPDATED and points added 
                    #dow_ba = get_days_of_week(get_json_ba)
                    #dow_op = get_days_of_week(get_json_op)
                    #opId_ba = get_optibus_id(get_json_ba)
                    #opId_op = get_optibus_id(get_json_op)






                    #json_data_list_ba = create_json_list(get_services_json_ba, token_baseline, domain_name_ba)
                    #json_data_list_op = create_json_list(get_services_json_op, token_optimisation, domain_name_op)



                    #BASELINE : https://arriva-uk-bus-northwest.optibus.co/project/da336nrgv/schedules/EvltiNwWMS/gantt?type=duties
                    #OPTIMISATION: https://arriva-uk-bus-northwest.optibus.co/project/da336nrgv/schedules/bBIr4mZwjT/gantt?type=duties
                    #Baseline is inserting two service groups and optimisation inserting 3, so problematic as calculations are wrong, count number of list elements to match to mitigate this 




                check_serv_ba = catch_service_lists(json_data_list_ba, 'service', 'daysOfWeek')
                check_serv_op = catch_service_lists(json_data_list_op, 'service', 'daysOfWeek')

                #




                missing_days_ba, identifier_ba = return_assciated_Serv_days(check_serv_ba, 'Baseline')
                missing_days_op, identifier_op = return_assciated_Serv_days(check_serv_ba, 'Optimisation')


                if len(missing_days_ba) != 0:
                    st.error(f"API Error Occuring for **{missing_days_ba}** on **{identifier_ba}** schedule for ****")
                    st.stop()
                elif len(missing_days_ba) != 0:
                    st.error(f"API Error Occuring for **{missing_days_op}** on **{identifier_op}** schedule for ****")
                    st.stop()

                service_groups_ba = retrieve_service_groups(json_data_list_ba)
                service_groups_op = retrieve_service_groups(json_data_list_op)











                list_ba = create_service_ids_list(json_data_list_ba)

                paid_time_list_ba, paid_time_list_sum_ba, paid_time_list_result_ba = create_meta_time_list(json_data_list_ba, 'crew', 'paid_time')
                paid_time_list_op, paid_time_list_sum_op, paid_time_list_result_op = create_meta_time_list(json_data_list_op, 'crew' , 'paid_time')


                platform_time_list_ba, platform_time_list_sum_ba, platform_time_list_result_ba = create_meta_time_list(json_data_list_ba, 'vehicle', 'platform_time')
                platform_time_list_op, platform_time_list_sum_op, platform_time_list_result_op = create_meta_time_list(json_data_list_op,'vehicle' , 'platform_time')

                #Create variables for duty counts 
                duty_count_list_ba, duty_count_list_sum_ba, duty_count_result_ba = create_meta_count_list(json_data_list_ba, 'crew', 'duties_count')
                duty_count_list_op, duty_count_list_sum_op, duty_count_result_op = create_meta_count_list(json_data_list_op,'crew',  'duties_count')

                def calculate_avg_paid_time(paid_time, duty_count):
                    avg_paid_time = [paid_time[i]/duty_count[i] for i in range(len(paid_time))]
                    return avg_paid_time

                avg_paid_time_ba = calculate_avg_paid_time(paid_time_list_result_ba,duty_count_result_ba)
                avg_paid_time_op = calculate_avg_paid_time(paid_time_list_result_op,duty_count_result_op)

                efficiency_ba = get_sch_eff(platform_time_list_result_ba, paid_time_list_result_ba)
                efficiency_op = get_sch_eff(platform_time_list_result_op, paid_time_list_result_op)

                duty_count_diff = calculate_duty_diff(duty_count_list_sum_ba, duty_count_list_sum_op)
                pt_diff = calculate_paid_time_diff(paid_time_list_sum_ba, paid_time_list_sum_op)  

                #Vars for advanced dataframe: 
                #create function for changeover_count (crew_stats)
                changeover_count_list_ba, changeover_count_sum_ba, changeover_count_result_ba = create_meta_count_list(json_data_list_ba,'crew', 'changeover_count')
                changeover_count_list_op, changeover_count_sum_op, changeover_count_result_op = create_meta_count_list(json_data_list_op,'crew' ,'changeover_count')

                #create function for standby_time (crew_stats)
                standby_time_list_ba, standby_time_list_sum_ba, standby_time_list_result_ba = create_meta_time_list(json_data_list_ba, 'crew' , 'standby_time')
                standby_time_list_op, standby_time_list_sum_op, standby_time_list_result_op = create_meta_time_list(json_data_list_op,'crew' , 'standby_time')

                #create for split_count (crew_stats)
                split_count_list_ba, split_count_sum_ba, split_count_result_ba = create_meta_count_list(json_data_list_ba,'crew', 'split_count')
                split_count_list_op, split_count_sum_op, split_count_result_op = create_meta_count_list(json_data_list_op,'crew' ,'split_count')

                #create stat for pvr (vehicle schedule stats)
                pvr_count_list_ba, pvr_count_sum_ba, pvr_count_result_ba = create_meta_count_list(json_data_list_ba,'vehicle', 'pvr')
                pvr_count_list_op, pvr_count_sum_op, pvr_count_result_op = create_meta_count_list(json_data_list_op,'vehicle' ,'pvr')


                #Table for relief car stats only have one attribute - awaiting response from orlando
                reliefcar_count_list_ba, reliefcar_count_sum_ba, reliefcar_count_result_ba = create_meta_count_list(json_data_list_ba,'relief_vehicle', 'relief_vehicle_count')
                reliefcar_count_list_op, reliefcar_count_sum_op, reliefcar_count_result_op = create_meta_count_list(json_data_list_op,'relief_vehicle' ,'relief_vehicle_count')

                #TODO: get key for relief car time stat:
                #reliefcar_time_list_ba, reliefcar_time_list_sum_ba, reliefcar_time_list_result_ba = create_meta_time_list(json_data_list_ba, 'relief_vehicle' , 'time')
                #reliefcar_time_list_op, reliefcar_time_list_sum_op, reliefcar_time_list_result_op = create_meta_time_list(json_data_list_op,'relief_vehicle' , 'time')



                #paid_break_ba = create_paid_break_time_list(json_data_list_ba)
                #paid_break_op = create_paid_break_time_list(json_data_list_op)

                #TODO: IMprove this function
                def get_duty_types_for_services(json_data_list):
                    duty_type_dict_list = []

                    for d in json_data_list:
                        try:
                            duty_types = d['service']['stats']['crew_schedule_stats']['histograms']['duty_types']
                            duty_type_dict = {}

                            for duty in duty_types:
                                duty_type_dict[duty[0]] = duty[1]

                            duty_type_dict_list.append(duty_type_dict)

                        except KeyError:
                            st.warning('Cant find key')

                    return duty_type_dict_list

                duty_type_dict_list_ba = get_duty_types_for_services(json_data_list_ba)
                duty_type_dict_list_op = get_duty_types_for_services(json_data_list_op)

                            # Create an empty dataframe with the duty types as columns

                def create_duty_type_df(duty_type_dict_list, service_groups_list):
                    duty_types = set()
                    for d in duty_type_dict_list:
                        duty_types.update(d.keys())

                    df = pd.DataFrame(columns=sorted(list(duty_types)))

                    # Add each row to the dataframe
                    for i, d in enumerate(duty_type_dict_list):
                        row = {}
                        for duty_type in duty_types:
                            if duty_type in d:
                                row[duty_type] = d[duty_type]
                            else:
                                row[duty_type] = 0
                        df.loc[service_groups_list[i]] = row

                    return df 

                df_duty_types_ba = create_duty_type_df(duty_type_dict_list_ba, service_groups_ba)
                df_duty_types_op = create_duty_type_df(duty_type_dict_list_op, service_groups_op)





                def compare_dataframes(df1, df2):
                    # Find the common set of columns and rows
                    common_columns = set(df1.columns).intersection(set(df2.columns))
                    common_index = set(df1.index).intersection(set(df2.index))

                    # Insert missing columns as zero-filled
                    for col in set(df1.columns).symmetric_difference(set(df2.columns)):
                        if col in df1.columns:
                            df2[col] = 0
                        else:
                            df1[col] = 0

                    # Match the common rows and drop the unmatched rows
                    unmatched_rows = set()
                    for row in common_index:
                        if row not in df1.index or row not in df2.index:
                            unmatched_rows.add(row)
                    common_index = common_index - unmatched_rows

                    df1 = df1.loc[list(common_index), list(common_columns)]
                    df2 = df2.loc[list(common_index), list(common_columns)]

                    

                    # Compute the difference between the dataframes
                    diff_df = df1 - df2

                    # Add a message for any unmatched rows
                    if unmatched_rows:
                        message = f"The following rows were unmatched: {unmatched_rows}"
                    else:
                        message = "All rows matched"

                    return diff_df, message


                diff_df_duty_types, message_warning = compare_dataframes(df_duty_types_ba, df_duty_types_op)



                def align_dataframe_orders(df1, df2, df3):
                    ordered_index = df1.index  # get the row order from df1
                    df2 = df2.reindex(index=ordered_index)  # order the rows of df2
                    df3 = df3.reindex(index=ordered_index)  # order the rows of df3

                    ordered_cols = df1.columns  # get the column order from df1
                    df2 = df2.reindex(columns=ordered_cols)  # order the columns of df2
                    df3 = df3.reindex(columns=ordered_cols)  # order the columns of df3

                    return df1, df2, df3


                df_duty_types_ba, df_duty_types_op, diff_df_duty_types = align_dataframe_orders(df_duty_types_ba, df_duty_types_op, diff_df_duty_types)



                merged_df_duty_types = pd.concat([df_duty_types_ba, df_duty_types_op, diff_df_duty_types], axis=1, keys=['df_duty_types_ba', 'df_duty_types_op', 'diff_df_duty_types'])

                merged_df_duty_types = merged_df_duty_types.reset_index(drop=False)


                def create_list_of_custom_time_defs(json_data_list):
                    result = []
                    for d in json_data_list:
                        try:
                            names = []
                            for l in d['service']['stats']['crew_schedule_stats']['custom_time_definitions']:
                                if l['name'] not in names:
                                    names.append(l['name'])
                            result.append(names)
                        except KeyError:
                            continue

                    flattened_list = []
                    for sublist in result:
                        for item in sublist:
                            flattened_list.append(item)
                    return flattened_list


                custom_name_list = create_list_of_custom_time_defs(json_data_list_ba)
                custom_name_list_ope = create_list_of_custom_time_defs(json_data_list_op)

                shared_values = set()

                for value_a in custom_name_list:
                    for value_b in custom_name_list_ope:
                        if value_a == value_b:
                            shared_values.add(value_a)

                new_custom_list = st.multiselect('**Select Custom Time Definitions**', shared_values)

                st.info('please click submit again if you have changed the value in the selectbox', icon='🚨')


                def create_custom_def_list(json_data_list, custom_list):
                    result = []
                    for d in json_data_list:
                        inner_dict = {}
                        try:
                            for l in d['service']['stats']['crew_schedule_stats']['custom_time_definitions']:
                                if l['name'] in custom_list:
                                    if l['name'] in inner_dict:
                                        inner_dict[l['name']] += l['value']
                                    else:
                                        inner_dict[l['name']] = l['value']
                        except KeyError:
                            pass
                        if inner_dict:
                            result.append(inner_dict)
                    return result


                custom_vals_list = create_custom_def_list(json_data_list_ba, new_custom_list)
                custom_vals_list_op = create_custom_def_list(json_data_list_op, new_custom_list)

                #custom_def_a_ba = create_custom_def_list(json_data_list_ba)
                #custom_def_a_op = create_custom_def_list(json_data_list_op)


                service_days_dict={
                    1:'Sun',
                    2:'Mon',
                    3:'Tue',
                    4:'Wed',
                    5:'Thur',
                    6:'Fri',
                    7:'Sat'
                }



                list_ba = []
                list_op = []
                #list_diff = []
                len_df = len(service_groups_ba)
                dic_ba = {}
                dic_op = {}
                dic_difference = {}
                for i in range(len_df):

                    dic_ba[service_groups_ba[i]]={
                        'Duty Count': duty_count_list_ba[i],
                        #'Av. Paid Time (hh:mm)': avg_paid_time_ba[i],
                        'Paid Time (hh:mm)': paid_time_list_ba[i],
                        #'Paid Break': paid_break_ba[i],
                        'Platform Time (hh:mm)': platform_time_list_ba[i],
                        **(custom_vals_list[i] if custom_vals_list else {})
                        #'Expected Efficiency (%)': efficiency_ba[i]
                    }

                    dic_op[service_groups_op[i]]={
                        'Duty Count': duty_count_list_op[i],
                        #'Av. Paid Time (hh:mm)': avg_paid_time_op[i],
                        'Paid Time (hh:mm)': paid_time_list_op[i],
                        #'Paid Break': paid_break_op[i],
                        'Platform Time (hh:mm)': platform_time_list_op[i],
                        **(custom_vals_list_op[i] if custom_vals_list_op else {})
                        #'Expected Efficiency (%)': efficiency_op[i]
                    }


                    list_ba.append(dic_ba[service_groups_ba[i]])
                    list_op.append(dic_op[service_groups_op[i]])




                for index, dic in enumerate(list_ba):
                    dic["Av. Paid Time (hh:mm)"] = round(dic["Paid Time (hh:mm)"] / dic["Duty Count"], 2)
                    dic["Expected Efficiency (%)"] = round((dic["Platform Time (hh:mm)"] / dic["Paid Time (hh:mm)"]) * 100, 2)
                    list_ba[index] = dic

                for index, dic in enumerate(list_op):
                    dic["Av. Paid Time (hh:mm)"] = round(dic["Paid Time (hh:mm)"] / dic["Duty Count"], 2)
                    dic["Expected Efficiency (%)"] = round((dic["Platform Time (hh:mm)"] / dic["Paid Time (hh:mm)"]) * 100, 2)
                    list_op[index] = dic







                def transform_into_df(list,services, string):
                    df = pd.DataFrame(list).T
                    df.columns=services
                    df = df.add_suffix(f' - {string}')
                    return df
                df_ba = transform_into_df(list_ba,service_groups_ba, 'Baseline')
                df_op = transform_into_df(list_op,service_groups_op, 'Optimisation')

                merged_df = pd.concat([df_ba,df_op],axis=1)
                merged_df = merged_df.sort_index(axis=1)
                len_merged_df = len(merged_df.columns)

                for i in range(0, len_merged_df, 2):
                    baseline = merged_df.columns[i]
                    optimisation = merged_df.columns[i+1]
                    merged_df[baseline[:3] + 'zx_diff'] = merged_df[optimisation] - merged_df[baseline]

                merged_df = merged_df.sort_index(axis=1) 
                new_len_merged_df = len(merged_df.columns)
                name_list=[]
                for i in range(0, len(merged_df.columns), 3):
                    col = merged_df.iloc[:, i]
                    col_name = col.name.split(' - Baseline')[0] + ' - Difference'
                    name_list.append(col_name)
                #st.write(name_list)
                for i in range(2, len(merged_df.columns), 3):
                    col = merged_df.iloc[:, i]
                    col_name = name_list[(i-2)//3]
                    merged_df = merged_df.rename(columns={col.name:col_name})
                with st.expander('Preview Dataframe'):          
                    merged_df_copy = merged_df.copy()
                    merged_df = round(merged_df,2)    
                    merged_df_copy = round(merged_df_copy,2)
                    change_to_hours(merged_df_copy,'Paid Time (hh:mm)')    
                    change_to_hours(merged_df_copy,'Av. Paid Time (hh:mm)')
                    #change_to_hours(merged_df_copy,'Paid Break')
                    change_to_hours(merged_df_copy,'Platform Time (hh:mm)')  

                # Loop through columns and apply conversion to each column

                merged_df_col_list = list(merged_df.columns)


                values = ['Duty Count', 'Av. Paid Time', 'Paid Time (hh:mm)', 'Platform Time (hh:mm)', 'Expected Efficiency (%)']

                def common_keys(dict_list):
                    if not dict_list:
                        return []
                    keys = set(dict_list[0].keys())
                    for d in dict_list[1:]:
                        keys &= set(d.keys())
                    return list(keys)

                if custom_vals_list:
                    unique_keys = common_keys(custom_vals_list)
                    values.extend(unique_keys)

                    if time_formats == '[h]:mm' or time_formats == '[h].d':
                        for col in unique_keys:
                            if col not in merged_df_col_list: # Skip columns you don't want to convert
                                continue
                            merged_df[col] = merged_df[col].apply(lambda x: '{:d}:{:02d}'.format(*divmod(abs(int(x)), 60)) if not pd.isna(x) and x>=0 else ('0' if pd.isna(x) or x==0 else '-{:d}:{:02d}'.format(*divmod(abs(int(x)), 60))) if not pd.isna(x) else '')
                            merged_df[col] = merged_df[col].apply(lambda x: '{:.2f}'.format(float(x)/60) if not pd.isna(x) and x!=0 and x[0]=='-' else x)
                    else:
                        pass

                if time_formats == '[h]:mm':
                    for col in merged_df.columns:
                        if col not in merged_df_col_list: # Skip columns you don't want to convert
                            continue
                        merged_df.iloc[1:-1, merged_df.columns.get_loc(col)] = merged_df.iloc[1:-1, merged_df.columns.get_loc(col)].apply(lambda x: '{:d}:{:02d}'.format(*divmod(abs(int(x)), 60)) if not pd.isna(x) and x>=0 else ('0' if pd.isna(x) or x==0 else '-{:d}:{:02d}'.format(*divmod(abs(int(x)), 60))))

                    merged_df = merged_df.astype(str)

                    merged_df.iloc[0] = merged_df.iloc[0].apply(lambda x: x[:-2] if str(x).endswith(".0") else x)

                elif time_formats == '[h].d':
                    for col in merged_df.columns:
                        if col not in merged_df_col_list: # Skip columns you don't want to convert
                            continue
                        merged_df.iloc[1:-1, merged_df.columns.get_loc(col)] = merged_df.iloc[1:-1, merged_df.columns.get_loc(col)].apply(lambda x: '{:.2f}'.format(float(x)/60) if not pd.isna(x) and x>=0 else ('0' if pd.isna(x) or x==0 else '-{:.2f}'.format(abs(float(x))/60)))

                    merged_df = merged_df.astype(str)

                    merged_df.iloc[0] = merged_df.iloc[0].apply(lambda x: x[:-2] if str(x).endswith(".0") else x)

                else:
                    pass

                st.write(merged_df)



        ################################ TODO: Return duty types on another df

                # Creating the format for the output:
                    # Depot name - depot_name
                    # Combined Dataframe: merged_df

                trans = len(merged_df)
                transend = trans+6
                transfir = transend -1
                transin = transend +2 
                transinn = transin +1

                #Hide the progress bar after all elements rendered

                time.sleep(0) # sleep for 3 seconds

                my_bar.empty()



                def reformatting_efficiency_column(arriva_df):
                    arriva_df['Paid Hours'] = round(arriva_df['Paid Hours']/60,2)
                    arriva_df['Platform Hours'] = round(arriva_df['Platform Hours']/60,2)
                    return arriva_df

                depot_name = 'Optimisation Comparison - ' + depot_name
                buffer3 = BytesIO()
                with ExcelWriter(buffer3,engine='xlsxwriter') as writer:
                    merged_df.to_excel(writer,sheet_name='Results',index=0, startcol=1, startrow=5)
                    merged_df_duty_types.to_excel(writer, sheet_name='Duty Types', startrow=1, startcol=1)
                    workbook = writer.book # Access the workbook
                    worksheet= writer.sheets['Results']
                    worksheet2= writer.sheets['Duty Types'] # Access the Worksheet
                    header_list = merged_df.columns.values.tolist() # Generate list of headers
                    for i in range(0, len(header_list)):
                        worksheet.set_column(i+1, i, len(header_list[i]))
                        bold = workbook.add_format({'bold':True})
                    format = workbook.add_format({'border': 1})
                    worksheet.conditional_format('B6:Z'+str(transend), {'type': 'no_blanks','format': format})
                    worksheet2.conditional_format('B2:Z20', {'type': 'no_blanks','format': format})
                    worksheet.conditional_format('B6:B'+str(transend), {'type': 'no_blanks','format': bold})
                    baseline_list = ['C', 'F', 'I', 'L', 'O', 'R', 'U', 'AA']
                    opt_list = ['D', 'G', 'J', 'M', 'P', 'S', 'V', 'BB']
                    diff_list = ['E', 'H', 'K', 'N', 'Q', 'T', 'W', 'CC']
                    f, g, h, j, k, l, m, n = '','','','','','', '', ''
                    variable_list = [f, g, h, j, k, l, m, n]
                    def create_col_header_colour(col_list, var_list, colour_str):
                        for i in range(0, len(col_list)):
                            var_list[i] = workbook.add_format({'bg_color': colour_str})
                        for j in range(0, len(var_list)):
                            worksheet.conditional_format(f'{col_list[j]}6:{col_list[j]}6', {'type': 'no_blanks','format': var_list[j]})
                        return worksheet.conditional_format(f'{col_list[j]}6:{col_list[j]}6', {'type': 'no_blanks','format': var_list[j]})

                    create_col_header_colour(baseline_list, variable_list, '#E9CAA0')
                    create_col_header_colour(opt_list, variable_list, '#BEE0EC')
                    create_col_header_colour(diff_list, variable_list, '#ccfff2')
                    colour = workbook.add_format({'bg_color': '#DCDCDC'})
                    worksheet.conditional_format(f'B6:B'+str(transend), {'type': 'no_blanks','format': colour})

                    colour_good = workbook.add_format({'bg_color':'#A5D29F',
                                                'font_color': '#003300'})
                    colour_bad = workbook.add_format({'bg_color':'#FFC7CE',
                                                'font_color': '#9C0006'})
                    colour_neutral = workbook.add_format({'bg_color':'#fff9e6',
                                                'font_color': '#664d00'})
                    max_range = len(merged_df.columns) - 1
                    max_range = int(max_range/3)

                    if time_formats == 'minutes':
                        def values_assign_styles_for_heatmap(diff_list, colour_variable, criteria, minimum, first_cell, last_cell):
                            for i in range (0, max_range):
                                worksheet.conditional_format(f'{diff_list[i]}{first_cell}:{diff_list[i]}{last_cell}', {'type': 'cell',
                                'criteria': criteria,
                                'value': minimum,
                                'format': colour_variable})
                            return worksheet.conditional_format(f'{diff_list[i]}{first_cell}:{diff_list[i]}{last_cell}', {'type': 'cell',
                                'criteria': criteria,
                                'value': minimum,
                                'format': colour_variable})

                        #TODO: CHECK THESE AS Heatmap wrong on [h]:d
                        values_assign_styles_for_heatmap(diff_list, colour_good, '<', 0, 7, transfir)
                        values_assign_styles_for_heatmap(diff_list, colour_bad, '>', 0, 7, transfir)
                        values_assign_styles_for_heatmap(diff_list, colour_bad, '<', 0, transend, transend)
                        values_assign_styles_for_heatmap(diff_list, colour_good, '>', 0, transend, transend)
                        values_assign_styles_for_heatmap(diff_list, colour_neutral, '=', 0, 7, transend)



                    title = workbook.add_format({'font_size':'20', 'bold':True})
                    worksheet.write('B1',f'{depot_name}', title)
                    worksheet.write_url('B3', f'{schedule_URL_baseline}', string='Baseline Schedule')
                    worksheet.write_url('B4', f'{schedule_URL_optimisation}', string='Optimised Schedule')
                    italic = workbook.add_format({'italic':True}) 
                    worksheet.write('B'+str(transin), 'Platform Time = Bus Hours (Vehicle Hours)',italic)
                    worksheet.write('B16'+str(transinn), 'Efficiency = Platform Time/Paid Time *100',italic)
                    #TODO: Add change to hours format to download output






                    workbook.close()


    if download_run_optibus == 'run':
        st.download_button(
            label=f"Download the Optimisation Comparison",
            data=buffer3,
            file_name= f"{depot_name} .xlsx",
            mime="application/vnd.ms-excel")
