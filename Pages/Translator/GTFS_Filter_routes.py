
import streamlit as st
import pandas as pd
import os
from zipfile import ZipFile, ZIP_DEFLATED
from pandas import read_csv, DataFrame, concat
from time import time
import io

class Instructions:
    instructions = 'Upload the GTFS File and run the script to download the with filtered routes'
    link = 'https://optibus.atlassian.net/wiki/spaces/OP/pages/2123595829/GTFS+Scripts'

class Description:
    title = "GTFS - Filter Routes"
    description = "This is a script that enables you to filter routes on the uploaded GTFS file"
    icon = "https://cdn-icons-png.flaticon.com/512/1032/1032914.png"
    author = 'Lior Zachs'

def run():
    logger= st.expander('Logging debugging info')

    def main():
        
        input_file = st.file_uploader("Select GTFS zip file", type=['zip'])
        if input_file is not None:
            zip_file = ZipFile(input_file, 'r')
            routes_df = read_csv(zip_file.open('routes.txt'), header=0, dtype=str)
            routes_to_filter = st.multiselect("Select route_id (within routes.txt) to filter", routes_df['route_id'].unique().tolist())
            
            routes_to_filter = DataFrame(routes_to_filter, columns=['route_id'], dtype=str)
            zip_file_output = gtfs_filtering(zip_file, routes_to_filter.set_index('route_id'))
            output_bytes = write_output_GTFS(zip_file_output, f'{input_file.name[:-4]}_filter_routes.zip')
            st.download_button(
                label="Download output file",
                data=output_bytes,
                file_name=f'{input_file.name[:-4]}_filter_routes.zip',
                mime="application/zip"
            )

    def create_routes_list(a):
        b = []
        for i in a.split(','):
            b.append(i.strip())
        return(DataFrame(b, columns=['route_id'], dtype=str))

    def gtfs_filtering(zip_file, df_routes):
        input_file_list = zip_file.namelist()
        df = {}
        if 'routes.txt' not in input_file_list:
            st.error('\nThere is no routes file in this folder. Aborting.\n')
        logger.write('Reading routes file')
        df['routes'] = read_csv(zip_file.open('routes.txt'), header=0, dtype=str).join(df_routes, on='route_id', how='inner').reset_index(drop=True)
        if 'trips.txt' not in input_file_list:
            st.error('\nThere is no trips file in this folder. Aborting.\n')
        logger.write('Reading trips file')
        df['trips'] = read_csv(zip_file.open('trips.txt'), header=0, dtype=str).join(df_routes, on='route_id', how='inner').reset_index(drop=True)
        trips = read_csv(zip_file.open('trips.txt'), header=0, dtype=str).join(df_routes, on='route_id',																				 how='inner').reset_index(drop=True)
        df_trip_ids=trips['trip_id']
        trip_list=df_trip_ids.values.tolist()
        df_trips = DataFrame(trip_list, columns=['trip_id'], dtype=str)
        df_trips=df_trips.set_index('trip_id')
        if 'stop_times.txt' not in input_file_list:
            st.error('\nThere is no stop times file in this folder. Aborting.\n')
        logger.write('Reading stop times file')
        df['stop_times'] = read_csv(zip_file.open('stop_times.txt'), header=0, dtype=str).join(df_trips, on='trip_id', how='inner').reset_index(drop=True)
        if 'agency.txt' not in input_file_list:
            st.error('\nThere is no agency file in this folder. Aborting.\n')
        logger.write('Reading agency file')
        df['agency'] = pd.read_csv(zip_file.open('agency.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'stops.txt' not in input_file_list:
            st.error('\nThere is no stops file in this folder. Aborting.\n')
        logger.write('Reading stops file')
        df['stops'] = pd.read_csv(zip_file.open('stops.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'shapes.txt' in input_file_list:
            logger.write('Reading shapes file')
            df['shapes'] = pd.read_csv(zip_file.open('shapes.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'calendar.txt' in input_file_list:
            logger.write('Reading calendar file')
            df['calendar'] = pd.read_csv(zip_file.open('calendar.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'calendar_dates.txt' in input_file_list:
            logger.write('Reading calendar_dates file')
            df['calendar_dates'] = pd.read_csv(zip_file.open('calendar_dates.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'attributions.txt' in input_file_list:
            logger.write('Reading attributions file')
            df['attributions'] = pd.read_csv(zip_file.open('attributions.txt'), header=0, dtype=str).reset_index(drop=True)
        if 'fare_attributes.txt' in input_file_list:
            logger.write('Reading fare_attributes file')
            df['fare_attributes'] = pd.read_csv(zip_file.open('fare_attributes.txt'), header=0, dtype=str).reset_index(
                drop=True)
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
            df['service_alerts'] = pd.read_csv(zip_file.open('service_alerts.txt'), header=0, dtype=str).reset_index(
                drop=True)
        return(df)
        

    def write_output_GTFS(df, zip_file_name):
        output_bytes = io.BytesIO()
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
