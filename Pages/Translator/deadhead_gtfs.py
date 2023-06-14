import streamlit as st
import os
import io
import zipfile
import pandas as pd
from routingpy import MapboxValhalla
import itertools
import numpy as np
import geopy
import time

class Instructions:
    instructions = 'Upload the VDV452 File and run the scripts to perform different Actions for VDV452'
    link = 'https://optibus.atlassian.net/wiki/spaces/PE/pages/2540535858/deadhead+generator'

class Description:
    title = "GFTS Deadhead Generator"
    description = "This is a toolset which enables you to create a Deadhead Catalog from a GTFS file"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/GTFS_SVG_Icon_01.svg/1200px-GTFS_SVG_Icon_01.svg.png"
    author = 'Zacharie Chebance'


index = 0

def run():
    api_key = 'pk.eyJ1IjoiemFjaGFyaWVjaGViYW5jZSIsImEiOiJja3FodjU3d2gwMGdoMnhxM2ZmNjZkYXc5In0.CSFfUFU-zyK_K-wwYGyQ0g'
    max_threshold = 10
    min_threshold = 0.1
    st.title('GTFS Deadhead Generator')
    st.caption('You can use this tools to create a deadhead Catalogue. Please note, that the GTFS file must be directly compressed. If there is an extra folder in the .zip Archive it will fail and not find the files.')
    uploaded_file = st.file_uploader('Upload a GTFS zip file:', type=['zip'])


    def crow_distance(origin, destination):
        origin_lat, origin_lon = origin[1], origin[0]
        destination_lat, destination_lon = destination[1], destination[0]
        return geopy.distance.geodesic((origin_lat, origin_lon), (destination_lat, destination_lon)).km

    def get_routing(row, maxVal):
        global index
        index = index +1

        progress = index / maxVal
        text = str(index + maxVal)
        my_bar.progress(progress, text=text)
        origin, destination = row[0], row[1]
        origin_lat, origin_lon = origin[1], origin[0]
        destination_lat, destination_lon = destination[1], destination[0]
        time.sleep(0.5)
        route = client.directions(locations=[origin, destination], profile='bus')
        origin_id = stops[(stops.stop_lat == origin_lat) & (
                stops.stop_lon == origin_lon)].stop_id.values[0]
        destination_id = stops[(stops.stop_lat == destination_lat) & (
                stops.stop_lon == destination_lon)].stop_id.values[0]
        return [origin_id, destination_id, int(route.duration / 60), route.distance / 1000]


    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_path = 'temp.zip'
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            stops_input = zip_ref.open('stops.txt')
            stop_times_input = zip_ref.open('stop_times.txt')
        stops = pd.read_csv(stops_input)
        stop_times = pd.read_csv(stop_times_input)


        stop_times_grouped = stop_times.groupby('trip_id')
        stop_times_ids = pd.concat([stop_times_grouped.nth(0)[['stop_id']], stop_times_grouped.nth(-1)[['stop_id']]])[
            'stop_id'].drop_duplicates().tolist()
        stops = stops[stops.stop_id.isin(stop_times_ids)]
        lat_lon = stops[['stop_lat', 'stop_lon']].drop_duplicates()
        client = MapboxValhalla(api_key=api_key)
        coords = [[lon, lat] for lat, lon in lat_lon.values.tolist()]
        combinations = pd.DataFrame(
            [p for p in itertools.product(coords, repeat=2)])
        vec_crow_distance = np.vectorize(crow_distance)
        combinations['crow_distance'] = vec_crow_distance(combinations[0].values, combinations[1].values)
        combinations = combinations[(combinations.crow_distance < max_threshold) & (combinations.crow_distance > min_threshold) & (combinations[0] != combinations[1])]
        st.write(combinations.head(5))
        st.write(combinations.shape[0])
        # combinations = combinations[(combinations[0] != combinations[1])]
        max_val  = combinations.shape[0]*0.5
        st.write('Estimated time:', max_val)
        my_bar = st.progress(0, text='Progress')


        try:

            combinations[
                ['Origin Stop Id', 'Destination Stop Id', 'Travel Time', 'Distance']] = combinations.apply(
                lambda x: get_routing(x, max_val), axis=1, result_type='expand')

        except Exception as e:
            st.write(e)
            pass

        st.write('Combinations finished')
        columns = ['Start Time Range', 'End Time Range', '	Generate Time', 'Route Id', 'Origin Stop Name',
                   'Destination Stop Name',
                   'Days Of Week', 'Direction', 'Purpose', 'Alignment', 'Pre-Layover Time', 'Post-Layover Time',
                   'updatedAt']
        st.write('Columns finished')

        combinations = pd.concat([combinations, pd.DataFrame(columns=columns)])
        st.write('Combinations concat finished')


        st.write('Combinations drop finished')
        combinations = combinations.drop([0, 1, 'crow_distance'], axis=1)
        # Write DataFrame to BytesIO object
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combinations.to_excel(writer, index=False, sheet_name='Deadheads')

        # Retrieve the BytesIO object's content
        excel_data = output.getvalue()

        st.write('Excel finished')
        download = 1
        if download == 1:
            st.download_button("Download Excel File", output, 'Deadhead_Catalog' + '.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
