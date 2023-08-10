import streamlit as st
import zipfile
from io import BytesIO
import pdfplumber
import pandas as pd
import re
import base64
import io
import xlsxwriter
from datetime import datetime, timedelta
from collections import defaultdict
import openpyxl
import os
import numpy as np


class Instructions:
    instructions = 'Upload the zipped timetables, datum (PDF), stop_catalogue (EXCEL) and expohast (txt) and run the script to download a GTFS file'
    

class Description:
    title = "KarlsonBus Hastus export to GTFS"
    description = "This is a script that enables you to convert Hastus format which common in sweden into PDF"
    icon = "data:image/png;base64,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"
    author = 'Luke Norman'


def run():
    def map_days_new(daylist):
        days = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']
        # Transform string list to integers
        daylist = [int(i) for i in daylist]
        if sum(daylist) == 0:
            return '' # return empty string if no day is selected
        
        day_str = ''
        consecutive = False
        for i in range(7):
            # Start of consecutive days
            if daylist[i] == 1 and (i == 0 or daylist[i-1] == 0):
                day_str += days[i]
                if i < 6 and daylist[i+1] == 1:
                    day_str += '-'
                    consecutive = True
            # End of consecutive days
            elif daylist[i] == 1 and (i == 6 or daylist[i+1] == 0):
                if not consecutive:
                    day_str += days[i]
                else:
                    day_str += days[i]
                    consecutive = False
                if i < 6 and daylist[i+1] == 1:
                    day_str += ','
            # Non-consecutive days
            elif daylist[i] == 1 and daylist[i-1] == 1 and daylist[i+1] == 1:
                continue
            elif daylist[i] == 1:
                day_str += days[i]
                if i < 6 and daylist[i+1] == 1:
                    day_str += ','
        return day_str





    def map_days(day_code):

        """
        This function takes a string of number(s) representing days of the week and maps them to their corresponding day names.
        
        Parameters:
        day_code (str): A string of number(s) representing days of the week.

        Returns:
        str: A string of day name(s) corresponding to the input number(s).
        """

        # Initialize an empty list to collect the day(s)
        days_list = []
        
        # Define the map from integer characters to days
        day_map = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday"
        }
        
        # Convert the day code to a string to enable iteration over characters
        day_code_str = str(day_code)
        
        # If the code is a single character, map it to a day
        if len(day_code_str) == 1:
            days_list.append(day_map.get(day_code_str, day_code_str))
        
        # If the code has two characters, map it to a range of days
        elif len(day_code_str) == 2:
            start_day = day_map.get(day_code_str[0], day_code_str[0])
            end_day = day_map.get(day_code_str[1], day_code_str[1])
            days_list.append(f"{start_day}-{end_day}")
        
        # If the code has more than two characters, map each character to a day
        else:
            for char in day_code_str:
                day = day_map.get(char)
                if day:
                    days_list.append(day)
        
        # Join the collected day(s) into a string and return it
        return ", ".join(days_list)


    def extract_periods_dates(pdf_file):

        """
        This function extracts periods and dates from a PDF file.

        Parameters:
        pdf_file (file): The PDF file to extract data from.

        Returns:
        dict: A dictionary with periods as keys and lists of start and end dates as values.
        """

        periods_dates = defaultdict(list)
        period_re = re.compile(r"Period:\s*(\d+\(\d+\)\.\d+)\s*(.*)")
        date_re = re.compile(r"(\d{4}-\d{2}-\d{2})(?:\s*-\s*(\d{4}-\d{2}-\d{2}))?")
        date_format = "%Y-%m-%d"
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split("\n")
                current_period = None
                for line in lines:
                    period_match = period_re.search(line)
                    date_match = date_re.search(line)
                    if period_match:
                        current_period = period_match.group(1)
                    elif date_match and current_period:
                        start_date = datetime.strptime(date_match.group(1), date_format)
                        end_date = datetime.strptime(date_match.group(2) or date_match.group(1), date_format)
                        periods_dates[current_period].append((start_date, end_date))

        return periods_dates




    def load_pdf_from_zip(file):
        """
        This function extracts all PDF files from a ZIP file and extracts text from their pages.

        Parameters:
        file (file): The ZIP file to extract the PDF files from.

        Returns:
        list[dict]: A list of dictionaries, each containing a PDF file name, number of pages, extracted texts, and the identifier.
        """

        data_list = []
        with zipfile.ZipFile(BytesIO(file.getvalue()), 'r') as zipped_files:
            pdf_files = [file for file in zipped_files.namelist() if file.endswith('.pdf') and not file.startswith('__MACOSX/') and not '._' in file]

            for selected_pdf in pdf_files:
                data = {}
                data['selected_pdf'] = selected_pdf
                data['Identifier'] = '_'.join(selected_pdf.split('/')[-1].split('.')[0].split('_')[:2])  # Extract identifier from file name

                with zipped_files.open(selected_pdf, 'r') as pdf_file:
                    try:
                        pdf = pdfplumber.open(BytesIO(pdf_file.read()))
                    except Exception as e:
                        st.write(f"Failed to read {selected_pdf}. Error: {e}")
                        continue  # Skip the rest of the processing for this file

                    number_of_pages = len(pdf.pages)
                    data['number_of_pages'] = number_of_pages

                    pages_to_scrape = range(1, number_of_pages + 1)
                    data['pages_to_scrape'] = pages_to_scrape

                    for page_number in pages_to_scrape:
                        page = pdf.pages[page_number - 1]
                        text = page.extract_text()
                        if 'texts' not in data:
                            data['texts'] = []

                        # Now you can safely append to 'texts'
                        data['texts'].append(text)

                    pdf.close()

                data_list.append(data)

        return data_list

    def parse_text(text):
        # Split the text into lines
        lines = text.split('\n')

        # Initialize data structures
        trips = []
        current_trip = None

        for line in lines:
            # Split the line into parts
            parts = line.split(';')

            # Check if this line is a trip or a timepoint
            if parts[0] == 'trip':
                # If we were already recording a trip, add it to the list of trips
                if current_trip is not None:
                    trips.append(current_trip)

                # Start recording a new trip
                current_trip = {
                    'id': ';'.join(parts[2:4]),
                    'days': parts[5:12],
                    'distance': float(parts[12]) if parts[12] != 'NF' else None,
                    'vehicle_type': parts[13],
                    'timepoints': []
                }
            elif parts[0] == 'tp' and current_trip is not None:
                # Add a timepoint to the current trip
                current_trip['timepoints'].append({
                    'timepoint': parts[1] == '1',
                    'stop_id': parts[2],
                    'time': parts[3],
                    'distance': float(parts[4]) if parts[4] != 'NF' else None
                })

        # Don't forget to add the last trip
        if current_trip is not None:
            trips.append(current_trip)

        return pd.DataFrame(trips)






    def process_texts(data):
        """
        This function processes extracted texts to generate a data dictionary for creating a DataFrame.

        Parameters:
        data (dict): A dictionary containing extracted texts and identifier.

        Returns:
        DataFrame: A DataFrame generated from the data dictionary.
        """

        texts = data['texts']
        identifier = data['Identifier']

        columns = ['Avtalsnummer', 'Destinationskod', 'Tågnummer', 
                'Fordonstyp', 'Omlopp', 'Period', 'Inskränkningsperiod', 'Turnummer', 'Entreprenör', 'Dagar']
        excluded = ['Taxetyp', 'Skyltvariant', 'Turkod', 'Trafiktyp', 'Turtyp', 'Anmärkningar', 'Avstånd']
        data_dict = {column: [] for column in columns}
        data_dict['Identifier'] = []

        for text in texts:
            if 'Avtalsnummer' not in text:
                continue
            text = text[text.index('Avtalsnummer'):]
            text = text.replace('*', ' special')
            words = re.findall(r'\b(?:Avgår från|[^\s]+\*?[^\s]*)', text)
            start_processing = False
            active_key = None
            for word in words:
                if word == 'Avtalsnummer':
                    start_processing = True
                if start_processing:
                    if word in columns:
                        active_key = word
                    elif word in excluded or word in columns:
                        active_key = None
                    elif active_key:
                        data_dict[active_key].append(word)
                        if active_key == 'Dagar':  # if 'Dagar' is the last column in a row
                            data_dict['Identifier'].append(identifier)
                            
        # add Identifier when a row ends

            

        return pd.DataFrame(data_dict)

    def add_mapping_columns(df):
        # Split the Identifier on comma and take the first part for the Identifier_Part
        df['Identifier_Part'] = df['Identifier'].str.split('_').str[0]

        # Split the Identifier on comma and take the second part for the Direction
        df['Direction'] = df['Identifier'].str.split('_').str[1]

        # Create the new column by concatenating the Identifier_Part and TripNumber with semicolons
        df['Identifier_TripNumber'] = df['Identifier_Part'] + ';' + df['TripNumber'].astype(str)

        return df




    def map_periods(df, df_grouped):

        """
        This function maps the 'Period' and 'InsPer' columns of a DataFrame to a new 'PeriodMap' and 'InsPerMap' columns 
        using a dictionary generated from another DataFrame.

        Parameters:
        df (DataFrame): The DataFrame to map periods.
        df_grouped (DataFrame): The DataFrame to generate the mapping dictionary from.

        Returns:
        DataFrame: The DataFrame with mapped periods.
        """

        period_date_dict = pd.Series(df_grouped.Date.values, index=df_grouped.Period).to_dict()
        df['PeriodMap'] = df['Period'].map(period_date_dict)
        df['InsPerMap'] = df['Inskränkningsperiod'].map(period_date_dict)
        return df

    def translate_columns(df):

        """
        This function translates the column names of a DataFrame from Swedish to English.

        Parameters:
        df (DataFrame): The DataFrame to translate column names.

        Returns:
        DataFrame: The DataFrame with translated column names.
        """
    
        df = df.rename(columns={
            "Avtalsnummer": "ContractNumber",
            "Destinationskod": "DestinationCode",
            "Avgår från": "DeparturePoint",
            "Tågnummer": "TrainNumber",
            "Fordonstyp": "VehicleType",
            "Omlopp": "Block",
            "Period": "Period",
            "Inskränkningsperiod": "NoDrivePeriod",  
            "Turnummer": "TripNumber",
            "Entreprenör": "Entrep",  
            "Dagar": "Days"
        })
        df["Days"] = df["Days"].apply(lambda x: map_days(x) if pd.notna(x) else x)
        return df

    def map_df_trips_to_df_all(df_all, df_trips):
        # Rename 'id' column in df_trips to 'Identifier_TripNumber' for merging
        df_trips = df_trips.rename(columns={'id': 'Identifier_TripNumber'})
        st.write(df_trips)  
        
        # Merge df_all and df_trips on 'Identifier_TripNumber' column
        df_merged = pd.merge(df_all, df_trips, on='Identifier_TripNumber', how='inner')
        st.write(df_merged)   

        return df_merged

    def map_stops_to_timepoints(df_all, df_stops):
        # Convert stop data to a dictionary for faster lookup
        stop_dict = df_stops.set_index('ID')[['LATITUDE', 'LONGITUDE','STOP NAME']].to_dict('index')

        # Iterate over each row in df_all
        for i, row in df_all.iterrows():
            # Iterate over each timepoint in the 'timepoints' column
            for timepoint in row['timepoints']:
                # Check if the stop_id of the timepoint is in the stop data
                if timepoint['stop_id'] in stop_dict:
                    # Add the lat and long values to the timepoint
                    timepoint['lat'] = stop_dict[timepoint['stop_id']]['LATITUDE']
                    timepoint['long'] = stop_dict[timepoint['stop_id']]['LONGITUDE']
                    timepoint['stop_name'] = stop_dict[timepoint['stop_id']]['STOP NAME']
                    

        return df_all




    def generate_service_days(days_list):
        """
        This function takes a list of 7 strings (either '1's or '0's), and return a dict 
        with keys as days of the week (in GTFS format), and values as the corresponding strings.
        """
        days_gtfs = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        return dict(zip(days_gtfs, days_list))

    def create_gtfs(df_all):
        # Construct the service_id
        df_all['service_id'] = df_all.apply(lambda row: f"{row['days_map']}_{row['Period']}!{row['NoDrivePeriod']}", axis=1)

        # Replace the semicolon in the 'Identifier_TripNumber' with an underscore to form the 'trip_id'
        df_all['trip_id'] = df_all['Identifier_TripNumber'].str.replace(';', '_')

        def convert_time(time_str):
            time_int = int(time_str)
            hours = time_int // 100
            minutes = time_int % 100
            if hours >= 24:
                hours -= 24
            return f"{hours:02d}:{minutes:02d}:00"

        def process_timepoints(timepoints):
            for timepoint in timepoints:
                timepoint['time'] = convert_time(timepoint['time'])
            return timepoints

        df_all['timepoints'] = df_all['timepoints'].apply(process_timepoints)

        # Extract a list of unique stops with their latitudes, longitudes and names
        stops_dict = {}
        for timepoints in df_all['timepoints']:
            for timepoint in timepoints:
                if timepoint['stop_id'] not in stops_dict:
                    stops_dict[timepoint['stop_id']] = {
                        'stop_lat': timepoint['lat'],
                        'stop_lon': timepoint['long'],
                        'stop_name': timepoint['stop_name']
                    }

        # Convert the stops_dict to a dataframe
        df_stops = pd.DataFrame.from_dict(stops_dict, orient='index').reset_index()
        df_stops.columns = ['stop_id', 'stop_lat', 'stop_lon', 'stop_name']

        df_agency = pd.DataFrame({
            'agency_id': [1],
            'agency_name': ['Mock Agency'],
            'agency_url': ['http://www.mockagency.com'],
            'agency_timezone': ['America/New_York']
        })

        df_routes = df_all[['Identifier_Part']].drop_duplicates()
        df_routes.rename(columns={'Identifier_Part': 'route_id'}, inplace=True)
        df_routes['agency_id'] = 1
        df_routes['route_short_name'] = 'Route ' + df_routes['route_id'].astype(str)
        df_routes['route_long_name'] = 'Long name for Route ' + df_routes['route_id'].astype(str)
        df_routes['route_id'] = df_routes['route_id']

        # Adjust the 'Direction' by subtracting 1, then add it to the dataframe as 'direction_id'
        df_trips = df_all[['Identifier_Part', 'service_id', 'trip_id', 'Direction']].copy()
        df_trips.rename(columns={'Identifier_Part': 'route_id', 'Direction': 'direction_id'}, inplace=True)
        df_trips['direction_id'] = df_trips['direction_id'].astype(int) - 1

        def create_stop_times(row):
            trip_ids = []
            arrival_times = []
            departure_times = []
            stop_ids = []
            stop_sequences = []
            timepoints = []
            for i, timepoint in enumerate(row['timepoints']):
                trip_ids.append(row['trip_id'])
                arrival_times.append(timepoint['time'])
                departure_times.append(timepoint['time'])
                stop_ids.append(timepoint['stop_id'])
                stop_sequences.append(i)
                timepoints.append(int(timepoint['timepoint']))  # Convert boolean to int
            df_stop_times = pd.DataFrame({
                'trip_id': trip_ids,
                'arrival_time': arrival_times,
                'departure_time': departure_times,
                'stop_id': stop_ids,
                'stop_sequence': stop_sequences,
                'timepoint': timepoints  # Add timepoint field
            })
            return df_stop_times

        df_stop_times_list = df_all.apply(create_stop_times, axis=1).tolist()
        df_stop_times = pd.concat(df_stop_times_list, ignore_index=True)

        df_agency.to_csv('agency.txt', index=False)
        df_routes.to_csv('routes.txt', index=False)
        df_trips.to_csv('trips.txt', index=False)
        df_stop_times.to_csv('stop_times.txt', index=False)
        df_stops.to_csv('stops.txt', index=False)

        # Add this part for creating calendar.txt
        df_calendar = df_all[['service_id', 'days']].copy()  # Create a copy to avoid modifying df_all
        df_calendar['days_str'] = df_calendar['days'].apply(lambda x: ''.join(x))  # Convert list of days to string
        df_calendar.drop_duplicates(subset=['service_id', 'days_str'], inplace=True)
        df_calendar['days'] = df_calendar['days_str'].apply(list)  # Convert string back to list of days
        df_calendar.drop(columns='days_str', inplace=True)  # Drop the temporary string column

        df_calendar['days'] = df_calendar['days'].apply(generate_service_days)
        df_calendar = pd.concat([df_calendar.drop(['days'], axis=1), df_calendar['days'].apply(pd.Series)], axis=1)
        df_calendar['start_date'] = '20230701'  # Please replace with your actual date
        df_calendar['end_date'] = '20230801'  # Please replace with your actual date
        df_calendar.to_csv('calendar.txt', index=False)

        import numpy as np

        def create_calendar_dates(row):
            service_id = row['service_id']
            active_periods = row['PeriodMap']
            inactive_periods = row['InsPerMap']

            active_dates = []
            if active_periods is not None and active_periods is not np.nan and isinstance(active_periods, list):  
                for start, end in active_periods:
                    start_date = start.date()  # Convert to date if it's a timestamp
                    end_date = end.date()  # Convert to date if it's a timestamp
                    active_dates.extend([d.strftime('%Y%m%d') for d in pd.date_range(start_date, end_date)])

            inactive_dates = []
            if inactive_periods is not None and inactive_periods is not np.nan and isinstance(inactive_periods, list):  
                for start, end in inactive_periods:
                    start_date = start.date()  # Convert to date if it's a timestamp
                    end_date = end.date()  # Convert to date if it's a timestamp
                    inactive_dates.extend([d.strftime('%Y%m%d') for d in pd.date_range(start_date, end_date)])

            df_active = pd.DataFrame({
                'service_id': [service_id] * len(active_dates),
                'date': active_dates,
                'exception_type': [1] * len(active_dates)  # Active
            })

            df_inactive = pd.DataFrame({
                'service_id': [service_id] * len(inactive_dates),
                'date': inactive_dates,
                'exception_type': [2] * len(inactive_dates)  # Inactive
            })

            return pd.concat([df_active, df_inactive], ignore_index=True)


        df_calendar_dates_list = df_all.apply(create_calendar_dates, axis=1).tolist()
        df_calendar_dates = pd.concat(df_calendar_dates_list, ignore_index=True)
        df_calendar_dates.to_csv('calendar_dates.txt', index=False)

        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.write('agency.txt')
            zf.write('routes.txt')
            zf.write('trips.txt')
            zf.write('stop_times.txt')
            zf.write('stops.txt')
            zf.write('calendar.txt')
            #TODO NEED TO VALIDATE WHERE THESE CALENDAR DATES COME INTO IN THE TIMEPLAN AND CONFIRM THE LOGIC FOR PERIOD AND INSPER IS CORRECT
            zf.write('calendar_dates.txt')

        memory_file.seek(0)
        
        return memory_file




    def export_to_excel(df):

        """
        This function exports a DataFrame to an Excel file and provides a download button.

        Parameters:
        df (DataFrame): The DataFrame to export.

        No return value.
        """

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1')

        st.download_button(
            label="Download data as Excel",
            data=output,
            file_name='data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def app():

        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'Form'

        if 'current_step' not in st.session_state:
            st.session_state['current_step'] = 1

        if 'uploaded_files' not in st.session_state:
            st.session_state['uploaded_files'] = [None, None, None, None]  # We have 4 file uploaders

        def set_form_step(action,step=None):
            if action == 'Next':
                st.session_state['current_step'] = st.session_state['current_step'] + 1
            if action == 'Back':
                st.session_state['current_step'] = st.session_state['current_step'] - 1
            if action == 'Jump':
                st.session_state['current_step'] = step

        def reset_and_rerun():
            st.session_state['current_view'] = 'Form'
            st.session_state['current_step'] = 1
            st.session_state['uploaded_files'] = [None, None, None, None]
            

        def wizard_form_header():
            st.subheader(f'Hastus Data Processor - Step {st.session_state["current_step"]}')

            # determines button color which should be red when user is on that given step
            steps_colors = ['primary' if st.session_state['current_step'] == i else 'secondary' for i in range(1, 5)]
            steps_text = [f'Step {i}' if st.session_state['uploaded_files'][i-1] is None else f'Step {i} ✅' for i in range(1, 5)]

            step_cols = st.columns([.5,.85,.85,.85,.85,.5])    
            for i, (color, text) in enumerate(zip(steps_colors, steps_text), 1):
                step_cols[i].button(text, on_click=set_form_step, args=['Jump', i], type=color)

        def wizard_form_body():
            step = st.session_state['current_step']
            file_types = ['zip', 'pdf', 'xlsx', 'txt']  # Types of files for each step
            file_labels = ['Zipped PDFs of timetables', 'PDF period file for date mapping', 'Excel file with stop data', 'TXT file']
            
            file = st.file_uploader(f'Upload {file_labels[step-1]}', type=[file_types[step-1]], key=f'uploader_{step}')

            if file:
                st.session_state['uploaded_files'][step-1] = file
                st.success(f'File uploaded for step {step}')
        

        def wizard_form_footer():    
            form_footer_container = st.empty()
            with form_footer_container.container():
                
                disable_back_button = True if st.session_state['current_step'] == 1 else False
                disable_next_button = True if st.session_state['current_step'] == 4 else False
                
                form_footer_cols = st.columns([5,1,1,1.75])
                
                form_footer_cols[0].button('Cancel',on_click=reset_and_rerun)
                form_footer_cols[1].button('Back',on_click=set_form_step,args=['Back'],disabled=disable_back_button)
                form_footer_cols[2].button('Next',on_click=set_form_step,args=['Next'],disabled=disable_next_button)
                zip_file, pdf_file, stop_file, uploaded_file = st.session_state['uploaded_files']
                if zip_file and pdf_file and stop_file and uploaded_file:
                    disabled=False
                    style='primary'
                else:
                    disabled = True
                    style = 'secondary'
                
                if st.session_state['current_step'] == 4:
                    finish_button = form_footer_cols[3].button('Finish', disabled=disabled, type=style)
                    

                    if finish_button:
                        perform_processing()  # function that contains your data processing logic

        @st.spinner('In progress...')
        def perform_processing():
            zip_file, pdf_file, stop_file, uploaded_file = st.session_state['uploaded_files']

            if zip_file and pdf_file and stop_file and uploaded_file:
                text = uploaded_file.read().decode('utf-8')
                df_trips = parse_text(text)
                data_list = load_pdf_from_zip(zip_file)
                periods_dates = extract_periods_dates(pdf_file)
                df_periods_dates = pd.DataFrame([(period, date[0], date[1]) for period in periods_dates for date in periods_dates[period]], columns=["Period", "Start Date", "End Date"])
                df_periods_dates['Period'] = df_periods_dates['Period'].apply(lambda x: x.split('.')[1])
                df_grouped = df_periods_dates.groupby('Period').agg({'Start Date': list, 'End Date': list}).reset_index()
                df_grouped['Date'] = df_grouped.apply(lambda row: list(zip(row['Start Date'], row['End Date'])), axis=1)
                df_grouped = df_grouped.drop(['Start Date', 'End Date'], axis=1)

                df_stops = pd.read_excel(stop_file, usecols=[0, 1, 2, 3])

                dfs = []
                for data in data_list:
                    df = process_texts(data)
                    
                    df = map_periods(df, df_grouped)
                    dfs.append(df)

                df_all = pd.concat(dfs, ignore_index=True)
                st.write(df_all)

                
                df_all = translate_columns(df_all)
                st.write(df_all)
                df_all = add_mapping_columns(df_all)
                st.write(df_all)
                df_all = map_df_trips_to_df_all(df_all, df_trips)
                
                df_all = map_stops_to_timepoints(df_all, df_stops)
                # Define a function that checks if a timepoint has 'lat' or 'long' keys and returns the offending stop_ids.
                def missing_lat_long_stop_ids(timepoints):
                    return [tp['stop_id'] for tp in timepoints if 'lat' not in tp or 'long' not in tp]

                # Apply the function to df_all to get the missing stop_ids.
                df_all['missing_stop_ids'] = df_all['timepoints'].apply(missing_lat_long_stop_ids)

                # Filter out rows that have missing stop_ids and store in reference_df.
                reference_df = df_all[df_all['missing_stop_ids'].str.len() > 0].copy()
                st.write(len(reference_df))
                # Drop the 'missing_stop_ids' column from df_all and keep only rows without missing values.
                df_all = df_all[df_all['missing_stop_ids'].str.len() == 0].drop(columns='missing_stop_ids').copy()

                # Calculate count of unique unmapped stop_ids.
                unique_unmapped_stop_ids = set()
                reference_df['missing_stop_ids'].apply(unique_unmapped_stop_ids.update)
                count_unique_unmapped = len(unique_unmapped_stop_ids)
                unmapped_stop_ids_list = sorted(list(unique_unmapped_stop_ids))
                st.write(unmapped_stop_ids_list)

                st.write("Count of unique unmapped stop ids:", count_unique_unmapped)

            

                            # List of column names to exclude
                exclude_cols = ['PeriodMap', 'InsPerMap', 'days', 'timepoints']

                # List of column names to consider when identifying duplicates
                subset_cols = [col for col in df_all.columns if col not in exclude_cols]

                # Drop duplicates considering only the subset of columns
                df_all.drop_duplicates(subset=subset_cols, keep='first', inplace=True)
                df_all['days_map'] = df_all['days'].apply(map_days_new)

                # Call the function to create GTFS files
                
                export_to_excel(df_all)

        
                
                gtfs_memory = create_gtfs(df_all)
                st.download_button(
                    label="Download gtfs",
                    data=gtfs_memory,
                    file_name='gtfs.zip',
                    mime='application/zip'
        )
                
                pass  # placeholder

        def render_wizard_view():
            with st.expander('',expanded=True):
                wizard_form_header()
                st.markdown('---')
                wizard_form_body()
                st.markdown('---')
                wizard_form_footer()

        if st.session_state['current_view'] == 'Form':
            render_wizard_view()

    app()
    
