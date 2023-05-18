from time import time
import pandas as pd
from pandas import read_csv, ExcelWriter, DataFrame, read_table
from os.path import dirname, basename
from os import chdir, remove
from os.path import dirname, basename
from zipfile import ZipFile, ZIP_DEFLATED
import streamlit as st 
import os
import io

st.subheader('JDF to OGTFS Converter') 
logger = st.expander('logging outputs for debugging')

def run():
    start_time = time()
    
    logger.write(f'Packages imported in {(time() - start_time):.1f} seconds')
    
    uploaded_file = st.file_uploader('upload your file', type='zip')
    
    if uploaded_file is not None:
        with open("temp.zip", "wb") as f:
            f.write(uploaded_file.getbuffer())
        input_file = "temp.zip"
        time_0 = time()
        output_name = basename(input_file)[:-4]+'_OGTFS'
        JDF_dict={}
        agency = creating_agency_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_agency_file in {(time() - time_0):.1f} seconds')
        JDF_dict['agency']=agency
        StopTimes = creating_routes_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_routes_file in {(time() - time_0):.1f} seconds')
        JDF_dict['routes']=StopTimes
        stops = creating_stops_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_stops in {(time() - time_0):.1f} seconds')
        JDF_dict['stops']=stops
        stop_times = creating_stop_times_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_stop_times in {(time() - time_0):.1f} seconds')
        JDF_dict['stop_times'] = stop_times
        trips,calendar = creating_trips_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_trips in {(time() - time_0):.1f} seconds')
        JDF_dict['trips'] = trips
        JDF_dict['calendar'] = calendar
        vehicle_types = creating_vehicle_types_file()
        logger.write(f'\ncreating_vehicle_types in {(time() - time_0):.1f} seconds')
        JDF_dict['vehicle_types'] = vehicle_types
        trip_vehicle_types = creating_trip_vehicle_types_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_trip_vehicle_types in {(time() - time_0):.1f} seconds')
        JDF_dict['trip_vehicle_types'] = trip_vehicle_types
        excel_data = write_excel(JDF_dict)

        st.download_button(
            label="Download Excel file",
            data=excel_data,
            file_name='output.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
        logger.write(f'\nScript ran in {(time() - time_0):.1f} seconds')
        os.remove("temp.zip")


def creating_agency_file(zip_file):
    input_file_list = zip_file.namelist()
    if 'dopravci.txt' not in input_file_list:
        st.error('There is no dopravci(agencies) file in this folder. Aborting.')
        return
    logger.write('Reading dopravci(agencies) file')
    agency_jdf = pd.read_csv(zip_file.open('dopravci.txt'), header=None, dtype=str, encoding='unicode_escape').reset_index(
        drop=True)
    agency_jdf.columns=['agency_id','VAT_number','agency_name',"company type",'person name','Registered office','agency_timezone','Dispatching Phone','Information Phone','Fax','Email','agency_url','Carrier Resolution']
    agency=agency_jdf[['agency_id','agency_name','agency_url','agency_timezone']]
    agency['agency_url'] = agency.apply(lambda _: 'http://', axis=1)
    return agency

def creating_routes_file(zip_file):
    input_file_list = zip_file.namelist()
    if 'linky.txt' not in input_file_list:
        st.error('There is no linky(routes) file in this folder. Aborting.')
        return
    logger.write('Reading linky(agencies) file')
    routes_jdf = pd.read_csv(zip_file.open('linky.txt'), header=None, dtype=str,
                             encoding='unicode_escape').reset_index(drop=True)
    routes_jdf.columns=['route_id','route_long_name','agency_id','Line type','Means of transport','Exclusive JŘ','Group of Connections','Use of Markers','One-way JŘ','Reserve','License number','Validity of lic. from','Validity of lic. to','Validity of JŘ from','Validity of JŘ until','Carrier Resolution','Line Resolution']
    routes_jdf['route_short_name']=routes_jdf['route_id']
    routes_jdf['route_type'] = routes_jdf.apply(lambda _: '3', axis=1)
    routes=routes_jdf[['route_id','agency_id','route_short_name','route_long_name','route_type']]
    return routes

def creating_stops_file(zip_file):
    input_file_list = zip_file.namelist()
    if 'zastavky.txt' not in input_file_list:
        st.error('There is no zastavky(stops) file in this folder. Aborting.')
        return
    logger.write('Reading zastavky(stops) file')
    stops_jdf = pd.read_csv(zip_file.open('zastavky.txt'), header=None, dtype=str,
                            encoding='unicode_escape').reset_index(drop=True)
    stops_jdf.columns = ["stop_id", "Name of town", "Part of town", "Closer Place", "Name of town nearby", "State",
                         "Fixed Code 1", "Fixed Code 2", "Fixed Code 3", "Fixed Code 4", "Fixed Code 5", "Fixed Code 6"]
    stops_jdf['stop_name'] = stops_jdf[["Name of town", 'Part of town', 'Closer Place', 'State']].apply(
        lambda x: ', '.join(x.dropna()), axis=1)
    stops_jdf['stop_lat'] = stops_jdf.apply(lambda _: '', axis=1)
    stops_jdf['stop_lon'] = stops_jdf.apply(lambda _: '', axis=1)
    stops=stops_jdf[['stop_id','stop_name','stop_lat','stop_lon']]
    return stops

def creating_stop_times_file(zip_file):
    input_file_list = zip_file.namelist()
    if 'zasspoje.txt' not in input_file_list:
        st.error('There is no zasspoje(stop_times) file in this folder. Aborting.')
        return
    logger.write('Reading zasspoje(stop times) file ')
    #rest of your function
    stoptimes_jdf = pd.read_csv(zip_file.open('zasspoje.txt'), header=None, dtype=str,
                                encoding='unicode_escape').reset_index(drop=True)
    stoptimes_jdf.columns = ["Route Id", "trip Id", "Stop Sequence", "Point Id", "Marker code", "Site number",
                             "Fixe Code 1", "Fixe Code 2", "Fixe Code 3", "distance", "Time of Arrival",
                             "Dep Time", "Arrival time min.", "Departure time max.", 'Line resolution']
    stoptimes_jdf = stoptimes_jdf.loc[stoptimes_jdf['Dep Time'] != '<']
    stoptimes_jdf = stoptimes_jdf.loc[stoptimes_jdf['Dep Time'] != '|']
    stoptimes_jdf['Trip Id'] = stoptimes_jdf[["Route Id", 'trip Id']].apply(
        lambda x: '_'.join(x.dropna()), axis=1)
    stoptimes_jdf['trip Id'] = stoptimes_jdf['trip Id'].astype(int)
    stoptimes_jdf['even_trip'] = stoptimes_jdf['trip Id'].mod(2)
    stoptimes_jdf['trip Id'] = stoptimes_jdf['trip Id'].astype(str)
    stoptimes_jdf['even_trip'] = stoptimes_jdf['even_trip'].astype(str)
    even_trips = stoptimes_jdf.loc[stoptimes_jdf['even_trip'] == '0']
    seq = -1
    save = 0
    lst = []
    for index, row in even_trips.iterrows():
        new_save = row["Trip Id"]
        if save == new_save:
            seq += 1
            lst.append(seq)
        else:
            seq = 0
            lst.append(seq)
        save = new_save
    se = pd.Series(lst)
    even_trips['Sequence'] = se.values
    even_trips['Sequence'] = even_trips['Sequence'].astype(str)
    even_trips = even_trips[["Trip Id", "Dep Time", "Time of Arrival", "Point Id", "Sequence", "distance"]]
    odd_trips = stoptimes_jdf.loc[stoptimes_jdf['even_trip'] != '0']
    seq = -1
    save = 0
    lst = []
    for index, row in odd_trips.iterrows():
        new_save = row["Trip Id"]
        if save == new_save:
            seq += 1
            lst.append(seq)
        else:
            seq = 0
            lst.append(seq)
        save = new_save
    se = pd.Series(lst)
    odd_trips['Sequence'] = se.values
    odd_trips['Sequence'] = odd_trips['Sequence'].astype(str)
    odd_trips = odd_trips[["Trip Id", "Dep Time", "Time of Arrival", "Point Id", "Sequence", "distance"]]
    odd_trips = odd_trips[["Trip Id", "Dep Time", "Time of Arrival", "Point Id", "Sequence", "distance"]]
    StopTimes = pd.concat([even_trips, odd_trips], axis=0, ignore_index=True, sort=False)
    StopTimes.loc[StopTimes['Time of Arrival'] != None, 'Time'] = StopTimes["Time of Arrival"]
    StopTimes['Time'] = StopTimes['Time'].fillna(StopTimes["Dep Time"])
    StopTimes['Time Point'] = 'FALSE'
    StopTimes = StopTimes[["Trip Id", "Time", "Point Id", "Time Point", "Sequence", "distance"]]
    StopTimes['Sequence Id'] = StopTimes.apply(lambda _: '', axis=1)
    StopTimes['tp'] = "FALSE"
    StopTimes = StopTimes[["Trip Id", "Time", "Point Id", "Time Point", "Sequence", 'Sequence Id', "distance", 'tp']]
    StopTimes['time_a'] = StopTimes['Time'].str[:2]
    StopTimes['time_b'] = StopTimes['Time'].str[-2:]
    StopTimes['Time_new'] = StopTimes[["time_a", 'time_b']].apply(
        lambda x: ':'.join(x.dropna()), axis=1)
    StopTimes = StopTimes[
        ["Trip Id", "Time_new", "Point Id", "Time Point", "Sequence", 'Sequence Id', "distance", 'tp']]
    StopTimes.columns = ["Trip Id", "Time", "Point Id", "Time Point", "Sequence", 'Sequence Id', "distance", 'tp']
    StopTimes.loc[StopTimes['Sequence'] == '0', 'Time Point'] = 'TRUE'
    dict = {}
    StopTimes['Sequence'] = StopTimes['Sequence'].astype(int)
    for index, row in StopTimes.iterrows():
        ID = row['Trip Id']
        if ID in dict.keys():
            if row['Sequence'] > dict[ID]:
                dict[ID] = row['Sequence']
        else:
            dict[ID] = row['Sequence']
    StopTimes['Sequence'] = StopTimes['Sequence'].astype(str)
    dict_df = pd.DataFrame({'Trip Id': dict.keys(),
                            'Max': dict.values()})
    StopTimes = pd.merge(StopTimes, dict_df, on='Trip Id')
    StopTimes['Max'] = StopTimes['Max'].astype(str)
    StopTimes.loc[StopTimes['Sequence'] == StopTimes['Max'], 'Time Point'] = 'TRUE'
    StopTimes['tp'] = StopTimes['Time Point']
    StopTimes.drop("Max", axis=1, inplace=True)
    StopTimes['departure_time']=StopTimes["Time"]
    stop_times=StopTimes[['Trip Id',"Time",'departure_time',"Point Id","Sequence"]]
    stop_times.columns=['trip_id','arrival_time','departure_time','stop_id','stop_sequence']
    return stop_times

def creating_trips_file(zip_file):
    input_file_list = zip_file.namelist()
    if 'spoje.txt' not in input_file_list:
        st.error('There is no spoje(trips) file in this folder. Aborting.')
        return
    logger.write('Reading spoje(trips) file')

    trips_jdf = pd.read_csv(zip_file.open('spoje.txt'), header=None, dtype=str, encoding='unicode_escape').reset_index(
        drop=True)
    trips_jdf.columns = ["Route Id", "trip Id", "Fixed Code 1", "Fixed Code 2", "Fixed Code 3", "Fixed Code 4",
                         "Fixed Code 5", "Fixed Code 6", "Fixed Code 7", "Fixed Code 8", "Fixed Code 9",
                         "Fixed Code 10", "Connection group code", "Line resolution"]
    trips_jdf['Id'] = trips_jdf[["Route Id", 'trip Id']].apply(
        lambda x: '_'.join(x.dropna()), axis=1)
    trips_jdf['trip Id'] = trips_jdf['trip Id'].astype(int)
    trips_jdf['even_trip'] = trips_jdf['trip Id'].mod(2)
    trips_jdf.loc[trips_jdf['even_trip'] == 0, 'Direction'] = '1'
    trips_jdf['Direction'] = trips_jdf['Direction'].fillna('0')
    if 'zasspoje.txt' not in input_file_list:
        st.error('There is no zasspoje(stop_times) file in this folder. Aborting.')
        return
    logger.write('Reading zasspoje(stop times) file in order to get origin & destination stops for trips file')
    # ... (rest of your code)
    stoptimes_jdf = pd.read_csv(zip_file.open('zasspoje.txt'), header=None, dtype=str,
                                encoding='unicode_escape').reset_index(drop=True)
    stoptimes_jdf.columns = ["Route Id", "trip Id", "Stop Sequence", "Stop id", "Marker code", "Site number",
                             "Fixe Code 1", "Fixe Code 2", "Fixe Code 3", "KM", "Arrival Time",
                             "Departure Time", "Arrival time min.", "Departure time max.", 'Line resolution']
    stoptimes_jdf['Id'] = stoptimes_jdf[["Route Id", 'trip Id']].apply(
        lambda x: '_'.join(x.dropna()), axis=1)
    stoptimes_jdf['trip Id'] = stoptimes_jdf['trip Id'].astype(int)
    stoptimes_jdf.drop(stoptimes_jdf.loc[stoptimes_jdf['Departure Time'] == "<"].index, inplace=True)
    stoptimes_jdf.drop(stoptimes_jdf.loc[stoptimes_jdf['Departure Time'] == "|"].index, inplace=True)
    stoptimes_jdf['even_trip'] = stoptimes_jdf['trip Id'].mod(2)
    even_trips = stoptimes_jdf.loc[stoptimes_jdf['even_trip'] == 0]
    seq = -1
    save = 0
    lst = []
    for index, row in even_trips.iterrows():
        new_save = row["Id"]
        if save == new_save:
            seq += 1
            lst.append(seq)
        else:
            seq = 0
            lst.append(seq)
        save = new_save
    se = pd.Series(lst)
    even_trips['Sequence'] = se.values
    even_trips = even_trips[["Id", "Stop id", "Departure Time", "Sequence", "Arrival Time", "KM"]]
    even_trips['Sequence'] = even_trips['Sequence'].astype(str)
    odd_trips = stoptimes_jdf.loc[stoptimes_jdf['even_trip'] != 0]
    seq = -1
    save = 0
    lst = []
    for index, row in odd_trips.iterrows():
        new_save = row["Id"]
        if save == new_save:
            seq += 1
            lst.append(seq)
        else:
            seq = 0
            lst.append(seq)
        save = new_save
    se = pd.Series(lst)
    odd_trips['Sequence'] = se.values
    odd_trips = odd_trips[["Id", "Stop id", "Departure Time", "Sequence", "Arrival Time", "KM"]]
    odd_trips['Sequence'] = odd_trips['Sequence'].astype(str)
    Stop_Times = pd.concat([even_trips, odd_trips], axis=0, ignore_index=True, sort=False)
    Stop_Times['Sequence'] = Stop_Times['Sequence'].astype(int)
    dict = {}
    dict_dist = {}
    for index, row in Stop_Times.iterrows():
        ID = row["Id"]
        if ID in dict.keys():
            current = dict[ID]
            if row["Sequence"] > current:
                dict[ID] = row["Sequence"]
                dict_dist[ID] = row["KM"]
        else:
            dict[ID] = row["Sequence"]
            dict_dist[ID] = row["KM"]
    dict_df = pd.DataFrame({'Id': dict.keys(),
                            'Max': dict.values()})
    Stop_Times = pd.merge(Stop_Times, dict_df, on='Id')
    dict = {}
    for index, row in Stop_Times.iterrows():
        ID = row["Id"]
        if ID in dict.keys():
            current = dict[ID]
            if row["Sequence"] < current:
                dict[ID] = row["Sequence"]
        else:
            dict[ID] = row["Sequence"]
    Stop_Times['Sequence'] = Stop_Times['Sequence'].astype(str)
    dict_df = pd.DataFrame({'Id': dict.keys(),
                            'Min': dict.values()})
    Stop_Times = pd.merge(Stop_Times, dict_df, on='Id')
    Stop_Times['Max'] = Stop_Times['Max'].astype(str)
    Stop_Times['Min'] = Stop_Times['Min'].astype(str)
    Stop_Times.loc[Stop_Times['Sequence'] == Stop_Times['Max'], 'Arrival'] = Stop_Times["Arrival Time"]
    Stop_Times.loc[Stop_Times['Sequence'] == Stop_Times['Max'], 'Destination Stop Id'] = Stop_Times["Stop id"]
    Stop_Times.loc[Stop_Times['Sequence'] == Stop_Times['Min'], 'Departure'] = Stop_Times["Departure Time"]
    Stop_Times.loc[Stop_Times['Sequence'] == Stop_Times['Min'], 'Origin Stop id'] = Stop_Times["Stop id"]
    Stop_Times = Stop_Times[["Id", 'Departure', 'Arrival', 'Destination Stop Id', 'Origin Stop id', "Arrival Time"]]
    origin = Stop_Times[["Id", 'Origin Stop id', 'Departure', "Arrival Time"]]
    origin = origin.dropna(subset=['Origin Stop id'])
    origin['Departure'] = origin['Departure'].fillna(origin["Arrival Time"])
    origin = origin[["Id", 'Origin Stop id', 'Departure']]
    Dest = Stop_Times[['Id', 'Destination Stop Id', "Arrival"]]
    Dest = Dest.dropna(subset=['Destination Stop Id'])
    origin_dest = pd.merge(origin, Dest, on='Id', how='inner')
    trips_jdf = pd.merge(trips_jdf, origin_dest, on='Id')
    trips_jdf["Vehicle Type Ids"] = 'Bus'
    dict_dist_df = pd.DataFrame({'Id': dict_dist.keys(),
                                 'Distance': dict_dist.values()})
    trips_jdf = pd.merge(trips_jdf, dict_dist_df, on='Id')
    days = trips_jdf[['Id', "Fixed Code 1", "Fixed Code 2", "Fixed Code 3", "Fixed Code 4",
                      "Fixed Code 5", "Fixed Code 6", "Fixed Code 7", "Fixed Code 8", "Fixed Code 9", "Fixed Code 10"]]
    if 'pevnykod.txt' not in input_file_list:
        st.error('There is no pevnykod file in this folder. Aborting.')
        return
    logger.write('Reading pevnykod file in order to get operational days')
    pevnykod_jdf = pd.read_csv(zip_file.open('pevnykod.txt'), header=None, dtype=str,
                               encoding='unicode_escape').reset_index(drop=True)
    pevnykod_jdf.columns = ["Fixed Code Number", "Fixed Code Designation", 'Reserve']
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == 'X', 'Days'] = 'WEEKDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '6', 'Days'] = 'SATURDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '+', 'Days'] = 'SUNDAYS_AND_PUBLIC_HOLIDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '1', 'Days'] = 'MONDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '2', 'Days'] = 'TUESDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '4', 'Days'] = 'THURSDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '5', 'Days'] = 'FRIDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '3', 'Days'] = 'WEDNESDAYS'
    pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '7', 'Days'] = 'SUNDAYS'
    pevnykod_jdf = pevnykod_jdf[['Fixed Code Number', 'Days']]
    pevnykod_jdf.loc[len(pevnykod_jdf.index)] = [None, None]
    pevnykod_jdf.columns = ["Fixed Code 1", 'Days1']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 1')
    pevnykod_jdf.columns = ["Fixed Code 2", 'Days2']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 2')
    pevnykod_jdf.columns = ["Fixed Code 3", 'Days3']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 3')
    pevnykod_jdf.columns = ["Fixed Code 4", 'Days4']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 4')
    pevnykod_jdf.columns = ["Fixed Code 5", 'Days5']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 5')
    pevnykod_jdf.columns = ["Fixed Code 6", 'Days6']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 6')
    pevnykod_jdf.columns = ["Fixed Code 7", 'Days7']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 7')
    pevnykod_jdf.columns = ["Fixed Code 8", 'Days8']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 8')
    pevnykod_jdf.columns = ["Fixed Code 9", 'Days9']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 9')
    pevnykod_jdf.columns = ["Fixed Code 10", 'Days10']
    days = pd.merge(days, pevnykod_jdf, on='Fixed Code 10')
    days['Days'] = days[
        ["Days1", "Days2", "Days3", "Days4", "Days5", "Days6", "Days7", "Days8", "Days9", "Days10"]].apply(
        lambda x: '_'.join(x.dropna()), axis=1)
    days = days[['Id', 'Days']]
    trips_jdf = pd.merge(trips_jdf, days, on='Id')
    Trips = trips_jdf[['Id', "Route Id", 'Direction', 'Origin Stop id', 'Destination Stop Id', 'Departure', 'Arrival',
                       'Vehicle Type Ids', 'Distance', 'Days']]
    Trips.columns = ['Id', "Sign", 'Direction', 'Origin Stop id', 'Destination Stop Id', 'Departure', 'Arrival',
                     'Vehicle Type Ids', 'Distance', 'Days']
    Trips['Region'] = Trips.apply(lambda _: '', axis=1)
    Trips['Catalog Number'] = Trips.apply(lambda _: '', axis=1)
    Trips['Alternative'] = Trips.apply(lambda _: '', axis=1)
    Trips['Day Offset'] = Trips.apply(lambda _: '0', axis=1)
    Trips['Existing'] = Trips.apply(lambda _: '', axis=1)
    Trips['Custom'] = Trips.apply(lambda _: '', axis=1)
    Trips['Boarding Time'] = Trips.apply(lambda _: '', axis=1)
    Trips['Boarding Time'] = Trips.apply(lambda _: '', axis=1)
    Trips['Offboarding Time'] = Trips.apply(lambda _: '', axis=1)
    Trips['Sub trip index'] = Trips.apply(lambda _: '', axis=1)
    Trips['Route Id'] = Trips[["Sign", 'Direction', 'Origin Stop id', 'Destination Stop Id', 'Distance']].apply(
        lambda x: '-'.join(x.dropna()), axis=1)
    Trips = Trips[
        ['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id', 'Destination Stop Id',
         'Day Offset', 'Departure', 'Arrival',
         'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days', 'Boarding Time', 'Offboarding Time',
         'Sub trip index', 'Route Id']]
    Trips['time_a'] = Trips['Departure'].str[:2]
    Trips['time_b'] = Trips['Departure'].str[-2:]
    Trips['Departure_new'] = Trips[["time_a", 'time_b']].apply(
        lambda x: ':'.join(x.dropna()), axis=1)
    Trips = Trips[
        ['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id', 'Destination Stop Id',
         'Day Offset', 'Departure_new', 'Arrival', 'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days',
         'Boarding Time', 'Offboarding Time', 'Sub trip index', 'Route Id']]
    Trips.columns = ['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id',
                     'Destination Stop Id',
                     'Day Offset', 'Departure', 'Arrival', 'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days',
                     'Boarding Time', 'Offboarding Time', 'Sub trip index', 'Route Id']
    Trips['time_a'] = Trips['Arrival'].str[:2]
    Trips['time_b'] = Trips['Arrival'].str[-2:]
    Trips['Arrival_new'] = Trips[["time_a", 'time_b']].apply(
        lambda x: ':'.join(x.dropna()), axis=1)
    Trips = Trips[
        ['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id', 'Destination Stop Id',
         'Day Offset', 'Departure', 'Arrival_new', 'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days',
         'Boarding Time', 'Offboarding Time', 'Sub trip index', 'Route Id']]
    Trips.loc[Trips['Days'] == '', 'Days'] = 'WEEKDAYS'
    Trips.columns = ['trip_id', 'Region', 'Catalog Number', "Sign", 'direction_id', 'Alternative', 'Origin Stop id',
                     'Destination Stop Id', 'Day Offset', 'Departure', 'Arrival', 'Vehicle Type Ids', 'Distance',
                     'Existing', 'Custom', 'days', 'Boarding Time', 'Offboarding Time', 'Sub trip index', 'Route Id']
    Trips[['route_id', 'old_trip']] = Trips['trip_id'].str.split('_', n=1, expand=True)
    Trips['len_id']=Trips["old_trip"].str.len()
    Trips['first'] = Trips['old_trip'].astype(str).str[0]
    Trips['len_id'] = Trips['len_id'].astype(str)
    Trips['first'] = Trips['first'].astype(str)
    Trips['concat_period'] = Trips[
        ["len_id", "first"]].apply(
        lambda x: ''.join(x.dropna()), axis=1)
    Trips.loc[Trips['concat_period'] == '32', 'period'] = '_WEEKENDS_AND_PUBLIC_HOLIDAYS'
    Trips.loc[Trips['concat_period'] == '33', 'period'] = '_SCHOOL_HOLIDAYS'
    Trips.loc[Trips['concat_period'] == '34', 'period'] = '_CHRISTMAS'
    Trips['period'] = Trips['period'].fillna('')
    input_file_list = zip_file.namelist()
    if 'caskody.txt' not in input_file_list:
        st.error('There is no caskody(calendar_dates) file in this folder. Aborting.')
        return
    logger.write('Reading caskody(calendar_dates) file')
    caskody_jdf = pd.read_csv(zip_file.open('caskody.txt'), header=None, dtype=str, encoding='unicode_escape').reset_index(
        drop=True)
    caskody_jdf.columns = ["Route Id", "trip Id", "Time code number", "Time code designation", "Time code type", "Date from",
                         "Date to", "Note", "Line resolution"]
    caskody_jdf['trip_id'] = caskody_jdf[["Route Id", 'trip Id']].apply(
        lambda x: '_'.join(x.dropna()), axis=1)
    caskody_jdf=caskody_jdf[['trip_id','Time code designation']]
    Trips=pd.merge(Trips,caskody_jdf,how='outer',on='trip_id')
    Trips.loc[Trips['Time code designation'] == '10', 'calendar'] = '_SCHOOL_DAYS_WORKING_DAYS'
    Trips.loc[Trips['Time code designation'] == '11', 'calendar'] = '_WORKING_DAYS_SCHOOL_HOLIDAY'
    Trips.loc[Trips['Time code designation'] == '25', 'calendar'] = '_WEEKDAYS_TRIPS'
    Trips.loc[Trips['Time code designation'] == '26', 'calendar'] = '_WEEKENDS_TRIPS'
    Trips.loc[Trips['Time code designation'] == '28', 'calendar'] = '_WEEKENDS_TRIPS'
    Trips.loc[Trips['Time code designation'] == '29', 'calendar'] = '_WEEKENDS_TRIPS'
    Trips.loc[Trips['Time code designation'] == '42', 'calendar'] = '_SCHOOL_TRAFFIC'
    Trips.loc[Trips['Time code designation'] == '32', 'calendar'] = '_HOLIDAY_TRAFFIC'
    Trips['calendar'] = Trips['calendar'].fillna('')
    Trips['service_id'] = Trips[
        ["days", "period", "calendar"]].apply(
        lambda x: ''.join(x.dropna()), axis=1)
    Trips.loc[Trips['service_id'] == 'SATURDAYS_SUNDAYS_AND_PUBLIC_HOLIDAYS', 'service_id'] = 'WEEKENDS_AND_PUBLIC_HOLIDAYS'
    trips=Trips[['route_id','service_id','trip_id','direction_id']]
    calendar=trips[['service_id']]
    calendar = calendar.drop_duplicates('service_id', keep='first')
    calendar.loc[calendar['service_id'].str.contains('WEEKDAYS')==True, 'monday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEEKDAYS') == True, 'tuesday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEEKDAYS') == True, 'wednesday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEEKDAYS') == True, 'thursday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEEKDAYS') == True, 'friday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('MONDAY') == True, 'monday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('TUESDAY') == True, 'tuesday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEDNESDAY') == True, 'wednesday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('THURSDAY') == True, 'thursday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('FRIDAY') == True, 'friday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('SATURDAY') == True, 'saturday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('SUNDAY') == True, 'sunday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEEKENDS') == True, 'sunday'] = '1'
    calendar.loc[calendar['service_id'].str.contains('WEEKENDS') == True, 'saturday'] = '1'
    calendar=calendar.fillna('0')
    trips = trips.drop_duplicates("trip_id", keep='first')
    return trips, calendar
    

def creating_vehicle_types_file():
    vehicle_types = {'vehicle_type_id': ['Bus'],'description':['Bus'],'name':['Bus']}
    vehicle_types = pd.DataFrame(vehicle_types)
    return vehicle_types

def creating_trip_vehicle_types_file(zip_file):
    input_file_list = zip_file.namelist()
    if 'spoje.txt' not in input_file_list:
        st.error('There is no spoje(trips) file in this folder. Aborting.')
        return
    logger.write('Reading spoje(trips) file')
    trips_jdf = pd.read_csv(zip_file.open('spoje.txt'), header=None, dtype=str, encoding='unicode_escape').reset_index(
        drop=True)
    trips_jdf.columns = ["Route Id", "trip Id", "Fixed Code 1", "Fixed Code 2", "Fixed Code 3", "Fixed Code 4",
                         "Fixed Code 5", "Fixed Code 6", "Fixed Code 7", "Fixed Code 8", "Fixed Code 9",
                         "Fixed Code 10", "Connection group code", "Line resolution"]
    trips_jdf['Id'] = trips_jdf[["Route Id", 'trip Id']].apply(
        lambda x: '_'.join(x.dropna()), axis=1)
   
    trip_vehicle_types=trips_jdf[['Id']]
    trip_vehicle_types['vehicle_type_id'] = trip_vehicle_types.apply(lambda _: 'Bus', axis=1)
    trip_vehicle_types.columns=['trip_id','vehicle_type_id']
    return trip_vehicle_types



def write_excel(table_array):
    time_0 = time()
    logger.write('Writing excel output')

    output = io.BytesIO()
    excel = pd.ExcelWriter(output, engine='xlsxwriter')
    header_format = excel.book.add_format({'bold': True, 'text_wrap': False, 'align': 'left'})

    for i in table_array:
        table_array[i].to_excel(excel, sheet_name=i, merge_cells=False, freeze_panes=[1, 0], index=False)
        for col_num, value in enumerate(table_array[i].columns.values):
            excel.sheets[i].write(0, col_num, value, header_format)
            excel.sheets[i].set_column(col_num, col_num,
                                       max(table_array[i][value].astype(str).str.len().max(), len(value) + 2))

    excel.close()
    output.seek(0)

    logger.write(f'Wrote excel output in {(time() - time_0):.1f} seconds')
    return output






