from time import time
start_time = time()
import pandas as pd
from pandas import read_csv, ExcelWriter, DataFrame, read_table
from os import chdir
from os.path import dirname, basename
from zipfile import ZipFile,ZIP_DEFLATED
import streamlit as st

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




