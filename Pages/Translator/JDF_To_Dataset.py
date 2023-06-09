from time import time
start_time = time()
import pandas as pd
from pandas import read_csv, ExcelWriter, DataFrame, read_table
from os import chdir, remove
from os.path import dirname, basename
from zipfile import ZipFile, ZIP_DEFLATED
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import streamlit as st
import io

class Instructions:
    instructions = 'Upload the JDF Zip File and run the script to download a Dataset file'
    link = 'https://optibus.atlassian.net/wiki/spaces/OP/pages/3117940752/JDF+Converting+Scripts#JDF-to-Dataset'

class Description:
    title = "JDF Into Dataset"
    description = "This is a script that enables you to convert JDF format which common in east Europe into Dataset, see confluence page for more instructions"
    icon = "data:image/png;base64,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"
    author = 'Lior Zacks'


def run():
    logger=st.expander('debugging info')

    def main():
        logger.write(f'Packages imported in {(time() - start_time):.1f} seconds')
        time_0 = time()
        input_file = st.file_uploader('Select JDF Zip File',type=['zip'])
        if input_file!=None:
            JDF_dict={}
            places = creating_places_file(ZipFile(input_file, 'r'))
            logger.write(f'\ncreating_places_file in {(time() - time_0):.1f} seconds')
            JDF_dict['Places']=places
            StopTimes = creating_StopTimes_file(ZipFile(input_file, 'r'))
            logger.write(f'\ncreating_StopTimes_file in {(time() - time_0):.1f} seconds')
            JDF_dict['StopTimes']=StopTimes
            trips = creating_trips_file(ZipFile(input_file, 'r'))
            logger.write(f'\ncreating_trips_file in {(time() - time_0):.1f} seconds')
            JDF_dict['Trips']=trips
            VehicleTypes = creating_VehicleTypes_file()
            logger.write(f'\ncreating_VehicleTypes in {(time() - time_0):.1f} seconds')
            JDF_dict['VehicleTypes']=VehicleTypes
            excel_data=write_excel(JDF_dict)
            st.download_button('Download File',data=excel_data,file_name='output.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            logger.write(f'\nScript ran in {(time() - time_0):.1f} seconds')

    def creating_places_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'zastavky.txt' not in input_file_list:
            exit('\nThere is no zastavky(stops) file in this folder. Aborting.\n')
        logger.write('Reading zastavky(stops) file')
        logger.write('Generating stops coordinates, this step can take around 10 minutes')
        stops_jdf = pd.read_csv(zip_file.open('zastavky.txt'), header=None, dtype=str,encoding='unicode_escape').reset_index(drop=True)
        stops_jdf.columns = ["Id","Name of town","Part of town","Closer Place","Name of town nearby","State","Fixed Code 1","Fixed Code 2","Fixed Code 3","Fixed Code 4","Fixed Code 5","Fixed Code 6"]
        stops_jdf['Description'] = stops_jdf[["Name of town", 'Part of town', 'Closer Place', 'State']].apply(lambda x: ', '.join(x.dropna()), axis=1)
        Places=stops_jdf
        Places['Address'] = Places.apply(lambda _: '', axis=1)
        Places['Type'] = Places.apply(lambda _: '', axis=1)
        geolocator = Nominatim(user_agent="my_request_1")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        state_df=Places['State']
        state=state_df.iloc[0]
        loc = geolocator.geocode(state)
        lat=loc.latitude
        lon=loc.longitude
        Places['location']=stops_jdf[["Name of town", 'Part of town', 'Closer Place', 'State']].apply(lambda x: ', '.join(x.dropna()), axis=1)
        geolocator = Nominatim(user_agent="my_request")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        Places['location2'] = Places['location'].apply(geocode)
        Places['Latitude'] = Places['location2'].apply(lambda x: x.latitude if x else lat)
        Places['Longitude'] = Places['location2'].apply(lambda x: x.longitude if x else lon)
        Places=Places[['Id', 'Description','Address','Latitude', 'Longitude','Type']]
        return Places

    def creating_StopTimes_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'zasspoje.txt' not in input_file_list:
            exit('\nThere is no zasspoje(stop_times) file in this folder. Aborting.\n')
        logger.write('Reading zasspoje(stop times) file ')
        stoptimes_jdf = pd.read_csv(zip_file.open('zasspoje.txt'), header=None, dtype=str,encoding='unicode_escape').reset_index(drop=True)
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
        even_trips= stoptimes_jdf.loc[stoptimes_jdf['even_trip'] == '0']
        seq=-1
        save=0
        lst=[]
        for index, row in even_trips.iterrows():
            new_save=row["Trip Id"]
            if save==new_save:
                seq+=1
                lst.append(seq)
            else:
                seq=0
                lst.append(seq)
            save=new_save
        se = pd.Series(lst)
        even_trips['Sequence'] = se.values
        even_trips['Sequence'] = even_trips['Sequence'].astype(str)
        even_trips=even_trips[["Trip Id","Dep Time","Time of Arrival","Point Id","Sequence","distance"]]
        odd_trips = stoptimes_jdf.loc[stoptimes_jdf['even_trip'] != '0']
        seq = -1
        save = 0
        lst = []
        for index, row in odd_trips.iterrows():
            new_save=row["Trip Id"]
            if save==new_save:
                seq+=1
                lst.append(seq)
            else:
                seq=0
                lst.append(seq)
            save=new_save
        se = pd.Series(lst)
        odd_trips['Sequence'] = se.values
        odd_trips['Sequence'] = odd_trips['Sequence'].astype(str)
        odd_trips=odd_trips[["Trip Id","Dep Time","Time of Arrival","Point Id","Sequence","distance"]]
        odd_trips = odd_trips[["Trip Id", "Dep Time", "Time of Arrival", "Point Id", "Sequence", "distance"]]
        StopTimes = pd.concat([even_trips, odd_trips], axis=0, ignore_index=True, sort=False)
        StopTimes.loc[StopTimes['Time of Arrival'] != None, 'Time'] = StopTimes["Time of Arrival"]
        StopTimes['Time'] = StopTimes['Time'].fillna(StopTimes["Dep Time"])
        StopTimes['Time Point']='FALSE'
        StopTimes = StopTimes[["Trip Id", "Time", "Point Id", "Time Point", "Sequence", "distance"]]
        StopTimes['Sequence Id'] = StopTimes.apply(lambda _: '', axis=1)
        StopTimes['tp'] = "FALSE"
        StopTimes = StopTimes[["Trip Id", "Time", "Point Id", "Time Point", "Sequence",'Sequence Id', "distance",'tp']]
        StopTimes['time_a']=StopTimes['Time'].str[:2]
        StopTimes['time_b'] = StopTimes['Time'].str[-2:]
        StopTimes['Time_new'] = StopTimes[["time_a", 'time_b']].apply(
            lambda x: ':'.join(x.dropna()), axis=1)
        StopTimes = StopTimes[["Trip Id", "Time_new", "Point Id", "Time Point", "Sequence", 'Sequence Id', "distance", 'tp']]
        StopTimes.columns= ["Trip Id", "Time", "Point Id", "Time Point", "Sequence", 'Sequence Id', "distance",'tp']
        StopTimes.loc[StopTimes['Sequence'] == '0', 'Time Point'] = 'TRUE'
        dict={}
        StopTimes['Sequence'] = StopTimes['Sequence'].astype(int)
        for index, row in StopTimes.iterrows():
            ID=row['Trip Id']
            if ID in dict.keys():
                if row['Sequence']>dict[ID]:
                    dict[ID]=row['Sequence']
            else:
                dict[ID] = row['Sequence']
        StopTimes['Sequence'] = StopTimes['Sequence'].astype(str)
        dict_df = pd.DataFrame({'Trip Id': dict.keys(),
                                'Max': dict.values()})
        StopTimes = pd.merge(StopTimes, dict_df, on='Trip Id')
        StopTimes['Max'] = StopTimes['Max'].astype(str)
        StopTimes.loc[StopTimes['Sequence'] == StopTimes['Max'], 'Time Point'] = 'TRUE'
        StopTimes['tp']=StopTimes['Time Point']
        StopTimes.drop("Max", axis=1, inplace=True)
        return StopTimes

    def creating_trips_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'spoje.txt' not in input_file_list:
            exit('\nThere is no spoje(trips) file in this folder. Aborting.\n')
        logger.write('Reading spoje(trips) file')
        trips_jdf = pd.read_csv(zip_file.open('spoje.txt'), header=None, dtype=str,encoding='unicode_escape').reset_index(drop=True)
        trips_jdf.columns = ["Route Id", "trip Id", "Fixed Code 1", "Fixed Code 2", "Fixed Code 3", "Fixed Code 4",
                             "Fixed Code 5", "Fixed Code 6", "Fixed Code 7", "Fixed Code 8", "Fixed Code 9", "Fixed Code 10","Connection group code","Line resolution"]
        trips_jdf['Id'] = trips_jdf[["Route Id", 'trip Id']].apply(
            lambda x: '_'.join(x.dropna()), axis=1)
        trips_jdf['trip Id'] = trips_jdf['trip Id'].astype(int)
        trips_jdf['even_trip']=trips_jdf['trip Id'].mod(2)
        trips_jdf.loc[trips_jdf['even_trip'] == 0, 'Direction'] = 'Inbound'
        trips_jdf['Direction']=trips_jdf['Direction'].fillna('Outbound')
        if 'zasspoje.txt' not in input_file_list:
            exit('\nThere is no zasspoje(stop_times) file in this folder. Aborting.\n')
        logger.write('Reading zasspoje(stop times) file in order to get origin & destination stops for trips file')
        stoptimes_jdf = pd.read_csv(zip_file.open('zasspoje.txt'), header=None, dtype=str,encoding='unicode_escape').reset_index(drop=True)
        stoptimes_jdf.columns = ["Route Id", "trip Id", "Stop Sequence", "Stop id", "Marker code", "Site number",
                             "Fixe Code 1", "Fixe Code 2", "Fixe Code 3", "KM", "Arrival Time",
                             "Departure Time", "Arrival time min.", "Departure time max.",'Line resolution']
        stoptimes_jdf['Id'] = stoptimes_jdf[["Route Id", 'trip Id']].apply(
            lambda x: '_'.join(x.dropna()), axis=1)
        stoptimes_jdf['trip Id'] = stoptimes_jdf['trip Id'].astype(int)
        stoptimes_jdf.drop(stoptimes_jdf.loc[stoptimes_jdf['Departure Time'] == "<"].index, inplace=True)
        stoptimes_jdf.drop(stoptimes_jdf.loc[stoptimes_jdf['Departure Time'] == "|"].index, inplace=True)
        stoptimes_jdf['even_trip'] = stoptimes_jdf['trip Id'].mod(2)
        even_trips= stoptimes_jdf.loc[stoptimes_jdf['even_trip'] == 0]
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
        even_trips = even_trips[["Id", "Stop id", "Departure Time","Sequence","Arrival Time","KM"]]
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
        odd_trips = odd_trips[["Id", "Stop id", "Departure Time", "Sequence", "Arrival Time","KM"]]
        odd_trips['Sequence'] = odd_trips['Sequence'].astype(str)
        Stop_Times = pd.concat([even_trips, odd_trips], axis=0, ignore_index=True, sort=False)
        Stop_Times['Sequence'] = Stop_Times['Sequence'].astype(int)
        dict={}
        dict_dist={}
        for index, row in Stop_Times.iterrows():
            ID=row["Id"]
            if ID in dict.keys():
                current=dict[ID]
                if row["Sequence"]>current:
                    dict[ID]=row["Sequence"]
                    dict_dist[ID]=row["KM"]
            else:
                dict[ID] = row["Sequence"]
                dict_dist[ID] = row["KM"]
        dict_df = pd.DataFrame({'Id': dict.keys(),
                                'Max': dict.values()})
        Stop_Times=pd.merge(Stop_Times,dict_df,on='Id')
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
        Stop_Times.loc[Stop_Times['Sequence'] == Stop_Times['Min'],'Departure'] = Stop_Times["Departure Time"]
        Stop_Times.loc[Stop_Times['Sequence'] == Stop_Times['Min'], 'Origin Stop id'] = Stop_Times["Stop id"]
        Stop_Times=Stop_Times[["Id",'Departure','Arrival','Destination Stop Id','Origin Stop id',"Arrival Time"]]
        origin=Stop_Times[["Id",'Origin Stop id','Departure',"Arrival Time"]]
        origin=origin.dropna(subset=['Origin Stop id'])
        origin['Departure'] = origin['Departure'].fillna(origin["Arrival Time"])
        origin = origin[["Id", 'Origin Stop id', 'Departure']]
        Dest=Stop_Times[['Id','Destination Stop Id',"Arrival"]]
        Dest = Dest.dropna(subset=['Destination Stop Id'])
        origin_dest = pd.merge(origin, Dest, on='Id', how='inner')
        trips_jdf = pd.merge(trips_jdf, origin_dest, on='Id')
        trips_jdf["Vehicle Type Ids"] = 'Bus'
        dict_dist_df = pd.DataFrame({'Id': dict_dist.keys(),
                                'Distance': dict_dist.values()})
        trips_jdf = pd.merge(trips_jdf, dict_dist_df, on='Id')
        days=trips_jdf[['Id',"Fixed Code 1", "Fixed Code 2", "Fixed Code 3", "Fixed Code 4",
                             "Fixed Code 5", "Fixed Code 6", "Fixed Code 7", "Fixed Code 8", "Fixed Code 9", "Fixed Code 10"]]
        if 'pevnykod.txt' not in input_file_list:
            exit('\nThere is no pevnykod file in this folder. Aborting.\n')
        logger.write('Reading pevnykod file in order to get operational days')
        pevnykod_jdf = pd.read_csv(zip_file.open('pevnykod.txt'), header=None, dtype=str,encoding='unicode_escape').reset_index(drop=True)
        pevnykod_jdf.columns = ["Fixed Code Number","Fixed Code Designation",'Reserve']
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == 'X', 'Days'] = '23456'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '6', 'Days'] = '7'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '+', 'Days'] = '1'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '1', 'Days'] = '2'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '2', 'Days'] = '3'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '4', 'Days'] = '5'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '5', 'Days'] = '6'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '3', 'Days'] = '4'
        pevnykod_jdf.loc[pevnykod_jdf['Fixed Code Designation'] == '7', 'Days'] = '1'
        pevnykod_jdf = pevnykod_jdf[['Fixed Code Number', 'Days']]
        pevnykod_jdf.loc[len(pevnykod_jdf.index)] = [None,None]
        pevnykod_jdf.columns = ["Fixed Code 1",'Days1']
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
        days['Days'] = days[["Days1","Days2","Days3","Days4","Days5","Days6","Days7","Days8","Days9","Days10"]].apply(
            lambda x: ''.join(x.dropna()), axis=1)
        days=days[['Id','Days']]
        trips_jdf = pd.merge(trips_jdf, days, on='Id')
        Trips=trips_jdf[['Id',"Route Id",'Direction','Origin Stop id','Destination Stop Id','Departure','Arrival','Vehicle Type Ids','Distance','Days']]
        Trips.columns=['Id', "Sign", 'Direction', 'Origin Stop id', 'Destination Stop Id', 'Departure', 'Arrival',
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
        Trips['Route Id'] = Trips[["Sign", 'Direction','Origin Stop id','Destination Stop Id','Distance']].apply(
            lambda x: '-'.join(x.dropna()), axis=1)
        Trips = Trips[['Id','Region','Catalog Number', "Sign", 'Direction','Alternative', 'Origin Stop id', 'Destination Stop Id','Day Offset', 'Departure', 'Arrival',
                           'Vehicle Type Ids', 'Distance','Existing','Custom','Days','Boarding Time','Offboarding Time','Sub trip index','Route Id']]
        Trips['time_a'] = Trips['Departure'].str[:2]
        Trips['time_b'] = Trips['Departure'].str[-2:]
        Trips['Departure_new'] = Trips[["time_a", 'time_b']].apply(
            lambda x: ':'.join(x.dropna()), axis=1)
        Trips = Trips[['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id', 'Destination Stop Id',
             'Day Offset', 'Departure_new', 'Arrival','Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days', 'Boarding Time','Offboarding Time', 'Sub trip index', 'Route Id']]
        Trips.columns=['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id', 'Destination Stop Id',
             'Day Offset', 'Departure', 'Arrival', 'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days',
             'Boarding Time','Offboarding Time', 'Sub trip index', 'Route Id']
        Trips['time_a'] = Trips['Arrival'].str[:2]
        Trips['time_b'] = Trips['Arrival'].str[-2:]
        Trips['Arrival_new'] = Trips[["time_a", 'time_b']].apply(
            lambda x: ':'.join(x.dropna()), axis=1)
        Trips = Trips[['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id', 'Destination Stop Id',
             'Day Offset', 'Departure', 'Arrival_new', 'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days',
             'Boarding Time','Offboarding Time', 'Sub trip index', 'Route Id']]
        Trips.loc[Trips['Days'] == '', 'Days'] = '23456'
        Trips.columns = ['Id', 'Region', 'Catalog Number', "Sign", 'Direction', 'Alternative', 'Origin Stop id','Destination Stop Id', 'Day Offset', 'Departure', 'Arrival', 'Vehicle Type Ids', 'Distance', 'Existing', 'Custom', 'Days','Boarding Time','Offboarding Time', 'Sub trip index', 'Route Id']
        return Trips
    def creating_VehicleTypes_file():
        VehicleTypes = {'Id': ['Bus'],'short_name':['Bus']}
        VehicleTypes = pd.DataFrame(VehicleTypes)
        return VehicleTypes

    def write_excel(table_array):
        time_0 = time()
        logger.write('\nWriting excel output')
        output=io.BytesIO()
        excel = ExcelWriter(output,engine='xlsxwriter')
        header_format = excel.book.add_format({'bold': True, 'text_wrap': False, 'align': 'left'})
        for i in table_array:
            table_array[i].to_excel(excel, sheet_name=i, merge_cells=False, freeze_panes=[1, 0], index=False)
            for col_num, value in enumerate(table_array[i].columns.values):
                excel.sheets[i].write(0, col_num, value, header_format)
                excel.sheets[i].set_column(col_num, col_num,
                                           max(table_array[i][value].astype(str).str.len().max(), len(value) + 2))
        excel.save()
        output.seek(0)
        logger.write(f'Wrote excel output in {(time() - time_0):.1f} seconds')
        return output
    main()


