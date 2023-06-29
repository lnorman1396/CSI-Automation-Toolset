import streamlit as st
import pandas as pd
import os
import zipfile
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from io import BytesIO

class Instructions:
    instructions = 'Upload the GTFS File and run the script to download the file with minimal service ID, if you have calendar_dates.txt file in your GTFS, you have to run first calendar GTFS script'
    link = 'https://optibus.atlassian.net/wiki/spaces/OP/pages/2123595829/GTFS+Scripts'

class Description:
    title = "GTFS Minimal Service IDs"
    description = "This is a script that condenses the GTFS File to use minimal service ids to optimise the file for import, for more info click on the Confluence link"
    icon = "https://optibus.atlassian.net/wiki/spaces/OP/pages/2123595829/GTFS+Scripts#4.-Minimal-number-of-service-IDs"
    author = 'Lior Zacks'

def run():



    logger = st.expander('log debugging messages')

    def main():
       
        uploaded_file = st.file_uploader("Choose a GTFS zip file", type="zip")
        if uploaded_file is not None:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_file_output = consolidate_function(zip_ref)
            logger.write('Processing...')
            output_filename = 'condenced_calendar.zip'
            output_bytes = write_output_GTFS(zip_file_output)
            st.download_button(
                label="Download output file",
                data=output_bytes.getvalue(),
                file_name="condenced_calendar.zip",
                mime="application/zip"
            )

    

    def consolidate_function(zip_file):
        input_file_list = zip_file.namelist()
        df = {}
        if 'calendar.txt' not in input_file_list:
            st.error('\nThere is no calendar file in this folder. Aborting.\n')
        logger.write('Reading calendar file')
        df['calendar'] = pd.read_csv(zip_file.open('calendar.txt'), header=0, dtype=str).reset_index(drop=True)
        calendar_df=df['calendar']
        zero_rows = calendar_df.loc[calendar_df['sunday'] == '0']
        zero_rows = zero_rows.loc[zero_rows['monday'] == '0']
        zero_rows = zero_rows.loc[zero_rows['tuesday'] == '0']
        zero_rows = zero_rows.loc[zero_rows['wednesday'] == '0']
        zero_rows = zero_rows.loc[zero_rows['thursday'] == '0']
        zero_rows = zero_rows.loc[zero_rows['friday'] == '0']
        zero_rows = zero_rows.loc[zero_rows['saturday'] == '0']
        left_joined = calendar_df.merge(
            zero_rows, how='left',
            on='service_id', indicator=True)
        left_only = left_joined.loc[left_joined['_merge'] == 'left_only', 'service_id']
        calendar_df = calendar_df[calendar_df['service_id'].isin(left_only)]
        calendar_df['day_sequence'] = calendar_df.apply(lambda x: '%s_%s_%s_%s_%s_%s_%s' % (str(x['monday']),str(x['tuesday']),str(x['wednesday']),str(x['thursday']),str(x['friday']),str(x['saturday']),str(x['sunday'])), axis=1)
        calendar_original=calendar_df
        calendar_df = calendar_df.drop_duplicates(subset='day_sequence', keep="first")
        merge_calendar=pd.merge(calendar_original,calendar_df,on='day_sequence')
        diffrent_services=merge_calendar.loc[merge_calendar['service_id_x'] != merge_calendar['service_id_y']]
        diffrent_services = diffrent_services.rename(columns={'service_id_x': 'service_id'})
        if 'trips.txt' not in input_file_list:
            st.error('\nThere is no trips file in this folder. Aborting.\n')
        logger.write('Reading trips file')
        df['trips'] = pd.read_csv(zip_file.open('trips.txt'), header=0, dtype=str).reset_index(drop=True)
        trips_df=df['trips']
        merge_trips_diff=pd.merge(trips_df, diffrent_services, on='service_id', how='inner')
        merge_trips_diff['service_id']=merge_trips_diff['service_id_y']
        trips = merge_trips_diff.filter(
            ['route_id', 'service_id', 'trip_id', 'shape_id', 'trip_headsign', 'trip_short_name', 'direction_id', 'block_id', 'wheelchair_accessible'],axis=1)
        left_joined = trips_df.merge(
            trips, how='left',
            on='trip_id', indicator=True)
        left_only = left_joined.loc[left_joined['_merge'] == 'left_only', 'trip_id']
        trips_2 = trips_df[trips_df['trip_id'].isin(left_only)]
        trips_final = pd.concat([trips, trips_2])
        df['trips']=trips_final
        calendar_df.drop('day_sequence', inplace=True, axis=1)
        df['calendar']=calendar_df
        if 'calendar_dates.txt' in input_file_list:
            logger.write('Reading calendar_dates file')
            df['calendar_dates'] = pd.read_csv(zip_file.open('calendar_dates.txt'), header=0, dtype=str).reset_index(drop=True)
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
        return df
    
    def write_output_GTFS(df):
        output_bytes = BytesIO()
        output_zip_file = ZipFile(output_bytes, 'w')
        
        for i in df:
            GTFS_file_name = i + '.txt'
            logger.write(f'Writing {GTFS_file_name} file')
            df[i].to_csv(GTFS_file_name, index=False)
            output_zip_file.write(GTFS_file_name, compress_type=ZIP_DEFLATED)
            os.remove(GTFS_file_name)
        
        output_zip_file.close()
        output_bytes.seek(0)
    
        return output_bytes

    
    main()
