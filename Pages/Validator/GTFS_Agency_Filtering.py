import streamlit as st
from time import time
from pandas import read_csv, DataFrame, concat
from os import chdir, remove
from os.path import basename, dirname
from zipfile import ZipFile, ZIP_DEFLATED
import io

class Description:
    title = "GTFS Agency Filter"
    description = "The following executable enables you to filter an agency or agencies within a GTFS file"
    icon = "data:image/png;base64,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"
    author = "Lior Zacks"



logger = st.expander('Logger for debugging')
def run():
    uploaded_file = st.file_uploader("Select GTFS zip file", type="zip")
    if uploaded_file is not None:
        with st.spinner('Reading and filtering GTFS file...'):
            agencies_to_filter = create_agency_list(st.text_input("Select agency_id (within agency.txt) to filter. For multiple agencies, separate them with a comma"))
            zip_file_output = gtfs_filtering(ZipFile(uploaded_file, 'r'), agencies_to_filter.set_index('agency_id'))
            st.success('Read and filtered GTFS file')

        with st.spinner('Writing GTFS zip file output...'):
            zip_file_name = f'{uploaded_file.name[:-4]}_filter_agency_{agencies_to_filter["agency_id"].str.cat(sep="_")}.zip'
            output = write_output_GTFS(zip_file_output)
            st.success('Wrote GTFS zip file output')
            st.download_button("Download Filtered GTFS", output)

def create_agency_list(a):
    b = []
    for i in a.split(','):
        b.append(i.strip())
    return(DataFrame(b, columns=['agency_id'], dtype=str))

def gtfs_filtering(zip_file, df_agencies):
	input_file_list = zip_file.namelist()
	df = {}
	if 'agency.txt' not in input_file_list:
		st.error('\nThere is no agency file in this folder. Aborting.\n')
	logger.write('Reading agency file')
	df['agency'] = read_csv(zip_file.open('agency.txt'), header=0, dtype=str).join(df_agencies, on='agency_id', how='inner').reset_index(drop=True)
	if 'routes.txt' not in input_file_list:
		st.error('\nThere is no routes file in this folder. Aborting.\n')
	logger.write('Reading routes file')
	df['routes'] = read_csv(zip_file.open('routes.txt'), header=0, dtype=str).join(df_agencies, on='agency_id', how='inner').reset_index(drop=True)
	if 'trips.txt' not in input_file_list:
		st.error('\nThere is no trips file in this folder. Aborting.\n')
	logger.write('Reading trips file')
	df['trips'] = read_csv(zip_file.open('trips.txt'), header=0, dtype=str).join(df['routes'][['route_id']].set_index('route_id'), on='route_id', how='inner').reset_index(drop=True)
	if 'stop_times.txt' not in input_file_list:
		st.error('\nThere is no stop_times file in this folder. Aborting.\n')
	logger.write('Reading stop_times file\t\t<- this can take a while as stop_times is a very large file')
	# stop_times.txt is treated differently from the other, because it can be so big.
	stop_times_list = []
	filtered_trips = df['trips'][['trip_id']].set_index('trip_id')
	for chunk in read_csv(zip_file.open('stop_times.txt'), header=0, dtype=str, chunksize=1000000):
		stop_times_list.append(chunk.join(filtered_trips, on='trip_id', how='inner').reset_index(drop=True))
	df['stop_times'] = concat(stop_times_list).reset_index(drop=True)
	if 'stops.txt' not in input_file_list:
		logger.write('\nThere is no stops file in this folder. Aborting.\n')
	logger.write('Reading stops file')
	stops = read_csv(zip_file.open('stops.txt'), header=0, dtype=str)
	stops_in_use = stops.join(df['stop_times'][['stop_id']].drop_duplicates().set_index('stop_id'), on='stop_id', how='inner').reset_index(drop=True)
	if 'parent_station' in stops_in_use.columns.values:
		df['stops'] = concat([stops_in_use, stops.join(stops_in_use[stops_in_use['parent_station'].notna()][['parent_station']].drop_duplicates().set_index('parent_station'), on='stop_id', how='inner')], ignore_index=True)
	else:
		df['stops'] = stops_in_use
	services = df['trips'][['service_id']].drop_duplicates().set_index('service_id')
	if 'calendar.txt' in input_file_list:
		logger.write('Reading calendar file')
		df['calendar'] = read_csv(zip_file.open('calendar.txt'), header=0, dtype=str).join(services, on='service_id', how='inner')
	if 'calendar_dates.txt' in input_file_list:
		logger.write('Reading calendar_dates file')
		df['calendar_dates'] = read_csv(zip_file.open('calendar_dates.txt'), header=0, dtype=str).join(services, on='service_id', how='inner')
	if 'shapes.txt' in input_file_list:
		logger.write('Reading shapes file')
		df['shapes'] = read_csv(zip_file.open('shapes.txt'), header=0, dtype=str).join(df['trips'][['shape_id']].drop_duplicates().set_index('shape_id'), on='shape_id', how='inner')
	if 'fare_rules.txt' in input_file_list:
		logger.write('Reading fare rules file')
		df['fare_rules'] = read_csv(zip_file.open('fare_rules.txt'), header=0, dtype=str).join(df['routes'][['route_id']].set_index('route_id'), on='route_id', how='inner').reset_index(drop=True)
		if 'fare_attributes.txt' in input_file_list:
			logger.write('Reading fare attributes file')
			df['fare_attributes'] = read_csv(zip_file.open('fare_attributes.txt'), header=0, dtype=str).join(df['fare_rules'][['fare_id']].drop_duplicates().set_index('fare_id'), on='fare_id', how='inner').reset_index(drop=True)
	for i in input_file_list:
		if (i[-4:] == '.txt') and (i[:-4] not in ['agency', 'routes', 'trips', 'stop_times', 'calendar', 'calendar_dates', 'shapes', 'stops', 'fare_rules', 'fare_attributes']):
			df[i[:-4]] = read_csv(zip_file.open(i), header=0, dtype=str)
	return(df)




def write_output_GTFS(df):
    output = io.BytesIO()
    output_zip_file = ZipFile(output, 'w')
    for i in df:
        GTFS_file_name = i + '.txt'
        print(f'Writing {GTFS_file_name} file')
        df[i].to_csv(GTFS_file_name, index=False)
        output_zip_file.write(GTFS_file_name, compress_type=ZIP_DEFLATED)
        remove(GTFS_file_name)
    output_zip_file.close()
    output.seek(0)
    return output

