from time import time
start_time = time()
import pandas as pd
from pandas import read_csv, ExcelWriter, DataFrame, read_table
from os import chdir
from os.path import dirname, basename
from zipfile import ZipFile,ZIP_DEFLATED
import streamlit as st

class Instructions:
    instructions = 'Upload the Hastus File and run the script to download a Dataset file'
    link = 'https://optibus.atlassian.net/wiki/spaces/OP/pages/3235151981/Hastus+Into+Data+set+Schedule+Scripts'

class Description:
    title = "Hastus Sweden Into Dataset"
    description = "This is a script that enables you to convert Hastus format which common in sweden into Dataset, see confluence page for more instructions"
    icon = "data:image/png;base64,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"
    author = 'Lior Zacks'

def run():
    logger=st.expander('Dubugging Info')


    def main():
        logger.write(f'Packages imported in {(time() - start_time):.1f} seconds')
        time_0 = time()
        input_file = st.file_uploader('Select Hastus ZipFile',type=['zip'])
        chdir(dirname(input_file))
        output_name = basename(input_file)[:-4]+'_Dataset'
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
        VehicleTypes = creating_VehicleTypes_file(ZipFile(input_file, 'r'))
        logger.write(f'\ncreating_VehicleTypes in {(time() - time_0):.1f} seconds')
        JDF_dict['VehicleTypes']=VehicleTypes
        write_excel(JDF_dict, output_name + '.xlsx')
        logger.write(f'\nScript ran in {(time() - time_0):.1f} seconds')

    def creating_places_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'hpltohast.txt' not in input_file_list:
            exit('\nThere is no hpltohast.txt(stops) file in this folder. Aborting.\n')
        logger.write('Reading hpltohast.txt(stops) file')
        stops = pd.read_csv(zip_file.open('hpltohast.txt'), header=None, dtype=str, encoding='unicode_escape',sep=';')
        stops.columns = ["1", "Id", "2", "3", "4"]
        stops['Description'] = stops[["2", '3']].apply(
            lambda x: ','.join(x.dropna()), axis=1)
        Places = stops[["Id",'Description']]
        Places['Address'] = ""
        Places['Latitude'] = ""
        Places['Longitude'] = ""
        Places['Type'] = ""
        return Places


    def creating_StopTimes_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'expohastFull.txt' not in input_file_list:
            exit('\nThere is no expohastFull file in this folder. Aborting.\n')
        logger.write('Reading expohastFull file')

        # Read the txt file into a DataFrame
        df = pd.read_csv(zip_file.open('expohastFull.txt'), header=None, dtype=str, encoding='unicode_escape')
        df = df[~df[0].isin(['gfall', 'block'])]
        df = df[0].str.split(";", expand=True)
        # Initialize empty lists to store the values from the "trip" rows
        trip_col3 = []
        trip_col4 = []

        # Iterate over the rows in the DataFrame
        for i in range(df.shape[0]):
            # Check if the current row is a "trip" row
            if df.iloc[i, 0] == "trip":
                # If it is, store the values from columns 3 and 4 in the lists
                trip_col3.append(df.iloc[i, 2])
                trip_col4.append(df.iloc[i, 3])
            # Check if the current row is a "tp" row
            elif df.iloc[i, 0] == "tp":
                # If it is, append the values from the lists to columns 3 and 4
                df.iloc[i, -1] = trip_col3[-1]
                df.iloc[i, 14] = trip_col4[-1]
        # Create two new DataFrames, one for the "trip" rows and one for the "tp" rows
        trip_df = df.loc[df[0] == "trip"]
        stop_df = df.loc[df[0] == "tp"]
        stop_df.columns = ["0", "Time Point", "Point Id", "Time", "distance",'5','6','7','8','9','10','11','12','13',"trip_id", "Sign"]
        stop_df['Trip Id'] = stop_df[["Sign", 'trip_id']].apply(
            lambda x: '_'.join(x.dropna()), axis=1)
        StopTimes = stop_df[["Trip Id", "Time", "Point Id","Time Point","distance"]]
        StopTimes['Time'] = StopTimes['Time'].str[0:2] + ':'+StopTimes['Time'].str[2:4]
        StopTimes.loc[StopTimes['Time Point'] == '1', 'Time Point'] = 'TRUE'
        StopTimes.loc[StopTimes['Time Point'] == '0', 'Time Point'] = 'FALSE'
        StopTimes['tp']=StopTimes['Time Point']
        seq=-1
        save=0
        lst=[]
        for index,row in StopTimes.iterrows():
            new_save=row['Trip Id']
            if save==new_save:
                seq+=1
                lst.append(seq)
            else:
                seq=0
                lst.append(seq)
            save=new_save
        se=pd.Series(lst)
        StopTimes['Sequence']=se.values
        StopTimes['Sequence'] = StopTimes['Sequence'].astype(str)
        StopTimes['Sequence Id']=''
        StopTimes = StopTimes[["Trip Id", "Time", "Point Id","Time Point",'Sequence','Sequence Id',"distance",'tp']]
        StopTimes=StopTimes.drop_duplicates()
        return StopTimes


    def creating_trips_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'expohastFull.txt' not in input_file_list:
            exit('\nThere is no expohastFull(trips) file in this folder. Aborting.\n')
        logger.write('Reading expohastFull(trips) file')

        # Read the txt file into a DataFrame
        df = pd.read_csv(zip_file.open('expohastFull.txt'), header=None,dtype=str,encoding='unicode_escape')
        df = df[~df[0].isin(['gfall','block'])]
        df = df[0].str.split(";", expand=True)
        # Initialize empty lists to store the values from the "trip" rows
        trip_col3 = []
        trip_col4 = []

        # Iterate over the rows in the DataFrame
        for i in range(df.shape[0]):
            # Check if the current row is a "trip" row
            if df.iloc[i, 0] == "trip":
                # If it is, store the values from columns 3 and 4 in the lists
                trip_col3.append(df.iloc[i, 2])
                trip_col4.append(df.iloc[i, 3])
            # Check if the current row is a "tp" row
            elif df.iloc[i, 0] == "tp":
                # If it is, append the values from the lists to columns 3 and 4
                df.iloc[i, -1] = trip_col3[-1]
                df.iloc[i, 14] = trip_col4[-1]
        # Create two new DataFrames, one for the "trip" rows and one for the "tp" rows
        trip_df = df.loc[df[0] == "trip"]
        tp_df = df.loc[df[0] == "tp"]
        trip_df.columns = ["1","2","Sign","trip_Id","3","Mon","Tue","Wed","Thu","Fri","Sat","Sun",'Distance','Vehicle Type Ids','4','5']
        trip_df['trip_Id'] = trip_df['trip_Id'].astype(int)
        trip_df['even_trip'] = trip_df['trip_Id'].mod(2)
        trip_df.loc[trip_df['even_trip'] == 0, 'Direction'] = 'Inbound'
        trip_df['Direction'] = trip_df['Direction'].fillna('Outbound')
        trip_df['trip_Id'] = trip_df['trip_Id'].astype(str)
        trip_df['Id'] = trip_df[["Sign", 'trip_Id']].apply(
            lambda x: '_'.join(x.dropna()), axis=1)
        trip_df = trip_df[["Id", "Sign", "Direction","Mon","Tue","Wed","Thu","Fri","Sat","Sun",'Distance','Vehicle Type Ids']]
        tp_df = tp_df.dropna(axis=1,how='all')
        tp_df.columns = ["0", "1", "stop_id", "time", "2", "3", "trip_id", "Sign"]
        tp_df['Id'] = tp_df[["Sign", 'trip_id']].apply(
            lambda x: '_'.join(x.dropna()), axis=1)
        seq = -1
        save = 0
        lst = []
        for index, row in tp_df.iterrows():
            new_save = row["Id"]
            if save == new_save:
                seq += 1
                lst.append(seq)
            else:
                seq = 0
                lst.append(seq)
            save = new_save
        se = pd.Series(lst)
        tp_df['Sequence'] = se.values
        tp_df = tp_df[["Id", "stop_id", "Sequence"]]
        tp_df['Sequence'] = tp_df['Sequence'].astype(int)
        dict = {}
        dict_dist = {}
        for index, row in tp_df.iterrows():
            ID = row["Id"]
            if ID in dict.keys():
                current = dict[ID]
                if row["Sequence"] > current:
                    dict[ID] = row["Sequence"]
                    dict_dist[ID] = row["stop_id"]
            else:
                dict[ID] = row["Sequence"]
                dict_dist[ID] = row["stop_id"]
        dict_df = pd.DataFrame({'Id': dict_dist.keys(),
                                'Destination Stop Id': dict_dist.values()})
        trip_df = pd.merge(trip_df, dict_df, on='Id')
        dict = {}
        dict_dist = {}
        for index, row in tp_df.iterrows():
            ID = row["Id"]
            if ID in dict.keys():
                current = dict[ID]
                if row["Sequence"] < current:
                    dict[ID] = row["Sequence"]
                    dict_dist[ID] = row["stop_id"]
            else:
                dict[ID] = row["Sequence"]
                dict_dist[ID] = row["stop_id"]
        dict_df = pd.DataFrame({'Id': dict_dist.keys(),
                                'Origin Stop id': dict_dist.values()})
        trip_df = pd.merge(trip_df, dict_df, on='Id')
        input_file_list = zip_file.namelist()
        if 'turhast.txt' not in input_file_list:
            exit('\nThere is no turhast(trips2) file in this folder. Aborting.\n')
        logger.write('Reading turhast.txt file')
        routes = pd.read_csv(zip_file.open('turhast.txt'), header=None, dtype=str, encoding='unicode_escape',sep=';')
        routes.columns = ["Sign", "trip_id", "1", "Departure","Arrival"]
        routes['Id'] = routes[["Sign", 'trip_id']].apply(
            lambda x: '_'.join(x.dropna()), axis=1)
        routes = routes[["Id","Departure", "Arrival" ]]
        Trips = pd.merge(trip_df, routes, on='Id')
        Trips['Alternative']=""
        Trips['Day Offset'] = "0"
        Trips['Existing'] = ""
        Trips['Custom'] = ""
        Trips['Boarding Time'] = ""
        Trips['Offboarding Time'] = ""
        Trips['Sub trip index'] = ""
        Trips['Region'] = ""
        Trips['Catalog Number'] = ""
        Trips['Route Id'] = Trips[["Sign", 'Direction', 'Origin Stop id', 'Destination Stop Id', 'Distance']].apply(
            lambda x: '-'.join(x.dropna()), axis=1)
        Trips.loc[Trips['Sun'] == '1', 'Sun_n'] = '1'
        Trips.loc[Trips['Sun'] != '1', 'Sun_n'] = ''
        Trips.loc[Trips['Mon'] == '1', 'Mon_n'] = '2'
        Trips.loc[Trips['Mon'] != '1', 'Mon_n'] = ''
        Trips.loc[Trips['Tue'] == '1', 'Tue_n'] = '3'
        Trips.loc[Trips['Tue'] != '1', 'Tue_n'] = ''
        Trips.loc[Trips['Wed'] == '1', 'Wed_n'] = '4'
        Trips.loc[Trips['Wed'] != '1', 'Wed_n'] = ''
        Trips.loc[Trips['Thu'] == '1', 'Thu_n'] = '5'
        Trips.loc[Trips['Thu'] != '1', 'Thu_n'] = ''
        Trips.loc[Trips['Fri'] == '1', 'Fri_n'] = '6'
        Trips.loc[Trips['Fri'] != '1', 'Fri_n'] = ''
        Trips.loc[Trips['Sat'] == '1', 'Sat_n'] = '7'
        Trips.loc[Trips['Sat'] != '1', 'Sat_n'] = ''
        Trips['Days'] = Trips[["Mon_n","Tue_n","Wed_n","Thu_n","Fri_n","Sat_n","Sun_n"]].apply(
            lambda x: ''.join(x.dropna()), axis=1)
        Trips = Trips[["Id", "Region", "Catalog Number", "Sign", "Direction", "Alternative", "Origin Stop id", "Destination Stop Id", "Day Offset", "Departure", "Arrival", "Vehicle Type Ids", "Distance", "Existing", "Custom", "Days", "Boarding Time", "Offboarding Time", "Sub trip index", "Route Id"]]
        Trips=Trips.drop_duplicates()
        return Trips

    def creating_VehicleTypes_file(zip_file):
        input_file_list = zip_file.namelist()
        if 'expohastFull.txt' not in input_file_list:
            exit('\nThere is no expohastFull file in this folder. Aborting.\n')
        logger.write('Reading expohastFull file')
        # Read the txt file into a DataFrame
        df = pd.read_csv(zip_file.open('expohastFull.txt'), header=None,dtype=str,encoding='unicode_escape')
        df = df[~df[0].isin(['gfall','block'])]
        df = df[0].str.split(";", expand=True)
        vehicles = df.loc[df[0] == "trip"]
        vehicles.columns = ["1","2","Sign","trip_Id","3","Sun","Mon","Tue","Wed","Thu","Fri","Sat",'Distance','Vehicle Type Ids','4','5']
        vehicles = vehicles.dropna(axis=1,how='all')
        VehicleTypes=vehicles[['Vehicle Type Ids']]
        VehicleTypes=VehicleTypes.drop_duplicates()
        VehicleTypes['Id']=VehicleTypes['Vehicle Type Ids']
        VehicleTypes.columns=['Id','short_name']
        return VehicleTypes

    def write_excel(table_array, output_file_name):
        time_0 = time()
        logger.write('\nWriting excel output')
        excel = ExcelWriter(output_file_name, engine='xlsxwriter')
        header_format = excel.book.add_format({'bold': True, 'text_wrap': False, 'align': 'left'})
        for i in table_array:
            table_array[i].to_excel(excel, sheet_name=i, merge_cells=False, freeze_panes=[1, 0], index=False)
            for col_num, value in enumerate(table_array[i].columns.values):
                excel.sheets[i].write(0, col_num, value, header_format)
                excel.sheets[i].set_column(col_num, col_num,
                                           max(table_array[i][value].astype(str).str.len().max(), len(value) + 2))
        excel.save()
        logger.write(f'Wrote excel output in {(time() - time_0):.1f} seconds')
    main()




