import streamlit as st
import pandas as pd
from os import chdir, remove
from os.path import dirname, basename
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
import io

class Description:
    title = "Calendar Conversion GTFS"
    description = "The script converts the GTFS calendar_dates.txt file into a calendar.txt file and adds the relevant service IDs to the service IDs that already exist in the calendar.txt file if there are any."
    link='https://optibus.atlassian.net/wiki/spaces/OP/pages/2123595829/GTFS+Scripts#3.-Convert-calendar_dates-into-a-calendar'
    icon = "https://cdn-icons-png.flaticon.com/512/1869/1869397.png"
    author = 'Lior Zacks'

def run():
    logger = st.expander('Log Debugging info')

    def main():
        
        uploaded_file = st.file_uploader("Select GTFS zip file", type="zip")
        if uploaded_file is not None:
            with ZipFile(uploaded_file, 'r') as zip_file:
                df = converting_function(zip_file)
                output_zip_file = write_output_GTFS(df)
                st.download_button(
                    label="Download converted GTFS zip file",
                    data=output_zip_file,
                    file_name='converted_gtfs.zip',
                    mime='application/zip'
                )

    def converting_function(zip_file):
        input_file_list = zip_file.namelist()
        df = {}
        if 'calendar_dates.txt' not in input_file_list:
            st.error('\nThere is no calendar_dates file in this folder. Aborting.\n')
        logger.write('Reading calendar_dates file')
        df['calendar_dates'] = pd.read_csv(zip_file.open('calendar_dates.txt'), header=0, dtype=str).reset_index(drop=True)
        calender_dates_df=df['calendar_dates']
        filter_exception=calender_dates_df.loc[calender_dates_df['exception_type']=='1'].reset_index(drop=True)
        if 'calendar.txt' not in input_file_list:
            filtered_services=filter_exception
            filtered_services['monday']='0'
            filtered_services['tuesday'] = '0'
            filtered_services['wednesday'] = '0'
            filtered_services['thursday'] = '0'
            filtered_services['friday'] = '0'
            filtered_services['saturday'] = '0'
            filtered_services['sunday'] = '0'
            filtered_services['start_date'] = '0'
            filtered_services['end_date'] = '0'
            filtered_services['date_type'] = pd.to_datetime(filtered_services['date'])
            filtered_services['day_in_the_week'] = filtered_services['date_type'].dt.day_of_week
            new_calendar = filtered_services.filter(
                ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date',
                'end_date', 'day_in_the_week'], axis=1)
            new_calendar.loc[new_calendar['day_in_the_week']==6, 'sunday'] = '1'
            new_calendar.loc[new_calendar['day_in_the_week'] == 0, 'monday'] = '1'
            new_calendar.loc[new_calendar['day_in_the_week'] == 1, 'tuesday'] = '1'
            new_calendar.loc[new_calendar['day_in_the_week'] == 2, 'wednesday'] = '1'
            new_calendar.loc[new_calendar['day_in_the_week'] == 3, 'thursday'] = '1'
            new_calendar.loc[new_calendar['day_in_the_week'] == 4, 'friday'] = '1'
            new_calendar.loc[new_calendar['day_in_the_week'] == 5, 'saturday'] = '1'
            logger.write(new_calendar)
            new_calendar['start_date']='20200101'
            new_calendar['end_date'] = '20300101'
            new_calendar = new_calendar.filter(
                ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date',
                'end_date'], axis=1)
        else:
            df['calendar_temp']=pd.read_csv(zip_file.open('calendar.txt'), header=0, dtype=str).reset_index(drop=True)
            calendar_df=df['calendar_temp']
            merge_services=pd.merge(filter_exception,calendar_df,on='service_id')
            filtered_services_1=merge_services.loc[merge_services['sunday'] == '0']
            filtered_services_1 = filtered_services_1.loc[filtered_services_1['monday'] == '0']
            filtered_services_1 = filtered_services_1.loc[filtered_services_1['tuesday'] == '0']
            filtered_services_1 = filtered_services_1.loc[filtered_services_1['wednesday'] == '0']
            filtered_services_1 = filtered_services_1.loc[filtered_services_1['thursday'] == '0']
            filtered_services_1 = filtered_services_1.loc[filtered_services_1['friday'] == '0']
            filtered_services_1 = filtered_services_1.loc[filtered_services_1['saturday'] == '0']
            left_joined = filter_exception.merge(
                calendar_df, how='left',
                on='service_id', indicator=True)
            left_only = left_joined.loc[left_joined['_merge'] == 'left_only', 'service_id']
            filtered_services_2 = filter_exception[filter_exception['service_id'].isin(left_only)]
            filtered_services=pd.concat([filtered_services_1,filtered_services_2])
            filtered_services['date_type']=pd.to_datetime(filtered_services['date'])
            filtered_services['day_in_the_week']=filtered_services['date_type'].dt.day_of_week
            filtered_services=filtered_services.drop_duplicates(subset=['service_id','day_in_the_week'],keep="first")
            new_calendar=filtered_services.filter(['service_id','monday','tuesday','wednesday','thursday','friday','saturday','sunday','start_date','end_date','day_in_the_week'], axis=1)
            new_calendar=new_calendar.fillna('0')
            days_by_service=new_calendar.groupby('service_id')['day_in_the_week'].apply(list)
            new_calendar.drop('day_in_the_week', inplace=True, axis=1)
            new_calendar = pd.merge(new_calendar, days_by_service, on='service_id')
            new_calendar=new_calendar.drop_duplicates(subset='service_id',keep="first")
            days_by_service= pd.DataFrame(new_calendar['day_in_the_week'].tolist())
            service_id=new_calendar.filter(['service_id'],axis=1).reset_index(drop=True)
            days_by_service['service_id']=service_id
            new_calendar=pd.merge(new_calendar,days_by_service,on='service_id')
            new_calendar.drop('day_in_the_week', inplace=True, axis=1)
            length=len(new_calendar.columns)
            len_days=length-10
            for column in range(len_days):
                new_calendar.loc[new_calendar[column]==6,'sunday']='1'
                new_calendar.loc[new_calendar[column]==0,'monday']='1'
                new_calendar.loc[new_calendar[column]==1,'tuesday']='1'
                new_calendar.loc[new_calendar[column]==2,'wednesday']='1'
                new_calendar.loc[new_calendar[column]==3,'thursday']='1'
                new_calendar.loc[new_calendar[column]==4,'friday']='1'
                new_calendar.loc[new_calendar[column]==5,'saturday']='1'
            new_calendar=new_calendar.filter(['service_id','monday','tuesday','wednesday','thursday','friday','saturday','sunday','start_date','end_date'], axis=1)
            left_joined = calendar_df.merge(
                filtered_services_1, how='left',
                on='service_id', indicator=True)
            left_only = left_joined.loc[left_joined['_merge'] == 'left_only', 'service_id']
            calender_no_zeros=calendar_df[calendar_df['service_id'].isin(left_only)]
            new_calendar = pd.concat([new_calendar,calender_no_zeros])
        new_calendar.drop_duplicates(subset=['service_id','monday','tuesday','wednesday','thursday','friday','saturday','sunday'])
        new_calendar = new_calendar.groupby('service_id').max().reset_index()
        df['calendar']=new_calendar
        if 'agency.txt' not in input_file_list:
            st.error('\nThere is no agency file in this folder. Aborting.\n')
        logger.write('Reading agency file')
        df['agency'] = pd.read_csv(zip_file.open('agency.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'routes.txt' not in input_file_list:
            st.error('\nThere is no routes file in this folder. Aborting.\n')
        logger.write('Reading routes file')
        df['routes'] = pd.read_csv(zip_file.open('routes.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'stops.txt' not in input_file_list:
            st.error('\nThere is no stops file in this folder. Aborting.\n')
        logger.write('Reading stops file')
        df['stops'] = pd.read_csv(zip_file.open('stops.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'stop_times.txt' not in input_file_list:
            st.error('\nThere is no stop_times file in this folder. Aborting.\n')
        logger.write('Reading stop_times file')
        df['stop_times'] = pd.read_csv(zip_file.open('stop_times.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'trips.txt' not in input_file_list:
            st.error('\nThere is no trips file in this folder. Aborting.\n')
        logger.write('Reading trips file')
        df['trips'] = pd.read_csv(zip_file.open('trips.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'shapes.txt' in input_file_list:
            logger.write('Reading shapes file')
            df['shapes'] = pd.read_csv(zip_file.open('shapes.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'attributions.txt' in input_file_list:
            logger.write('Reading attributions file')
            df['attributions'] = pd.read_csv(zip_file.open('attributions.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'fare_attributes.txt' in input_file_list:
            logger.write('Reading fare_attributes file')
            df['fare_attributes'] = pd.read_csv(zip_file.open('fare_attributes.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'fare_rules.txt' in input_file_list:
            logger.write('Reading fare_rules file')
            df['fare_rules'] = pd.read_csv(zip_file.open('fare_rules.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'feed_info.txt' in input_file_list:
            logger.write('Reading feed_info file')
            df['feed_info'] = pd.read_csv(zip_file.open('feed_info.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'frequencies.txt' in input_file_list:
            logger.write('Reading frequencies file')
            df['frequencies'] = pd.read_csv(zip_file.open('frequencies.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'levels.txt' in input_file_list:
            logger.write('Reading levels file')
            df['levels'] = pd.read_csv(zip_file.open('levels.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'pathways.txt' in input_file_list:
            logger.write('Reading pathways file')
            df['pathways'] = pd.read_csv(zip_file.open('pathways.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'transfers.txt' in input_file_list:
            logger.write('Reading transfers file')
            df['transfers'] = pd.read_csv(zip_file.open('transfers.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'translations.txt' in input_file_list:
            logger.write('Reading translations file')
            df['translations'] = pd.read_csv(zip_file.open('translations.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'service_alerts.txt' in input_file_list:
            logger.write('Reading service_alerts file')
            df['service_alerts'] = pd.read_csv(zip_file.open('service_alerts.txt'), header=0, dtype=str).reset_index(drop=True)
        df.pop('calendar_dates')
        if 'calendar.txt' in input_file_list:
            df.pop('calendar_temp')
        return df
        

    def write_output_GTFS(df):
        output_zip_file = io.BytesIO()
        with ZipFile(output_zip_file, 'w') as zipf:
            for i in df:
                GTFS_file_name = i + '.txt'
                logger.write(f'Writing {GTFS_file_name} file')
                df[i].to_csv(GTFS_file_name, index=False)
                zipf.write(GTFS_file_name, compress_type=ZIP_DEFLATED)
                remove(GTFS_file_name)
        output_zip_file.seek(0)
        return output_zip_file
    
    main()

