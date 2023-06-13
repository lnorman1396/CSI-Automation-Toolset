import streamlit as st
import os
import zipfile
import pandas as pd
from routingpy import MapboxValhalla
import itertools
import geopy.distance
import numpy as np
import tempfile

logger = st.expander('Logger for debugging')

class Instructions:
    instructions = 'Upload the VDV452 File and run the scripts to perform different Actions for VDV452'
    link = 'https://optibus.atlassian.net/wiki/spaces/PE/pages/2540535858/deadhead+generator'

class Description:
    title = "GFTS Deadhead Generator"
    description = "This is a toolset which enables you to create a Deadhead Catalog from a GTFS file"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/GTFS_SVG_Icon_01.svg/1200px-GTFS_SVG_Icon_01.svg.png"
    author = 'Zacharie Chebance'


def run():
    api_key = 'pk.eyJ1IjoiemFjaGFyaWVjaGViYW5jZSIsImEiOiJja3FodjU3d2gwMGdoMnhxM2ZmNjZkYXc5In0.CSFfUFU-zyK_K-wwYGyQ0g'
    st.title('GTFS Deadhead Generator')
    st.caption('You can use this tools to create a deadhead Catalogue. Please note, that the GTFS file must be directly compressed. If there is an extra folder in the .zip Archive it will fail and not find the files.')
    uploaded_file = st.file_uploader('Upload a GTFS zip file:', type=['zip'])
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location

        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            stops_input = zip_ref.open('stops.txt')
            stop_times_input = zip_ref.open('stop_times.txt')

    def get_routing(row):
        origin, destination = row[0], row[1]
        origin_lat, origin_lon = origin[1], origin[0]
        destination_lat, destination_lon = destination[1], destination[0]
        route = client.directions(locations=[origin, destination], profile='bus')
        origin_id = stops[(stops.stop_lat == origin_lat) & (
                stops.stop_lon == origin_lon)].stop_id.values[0]
        destination_id = stops[(stops.stop_lat == destination_lat) & (
                stops.stop_lon == destination_lon)].stop_id.values[0]
        return [origin_id, destination_id, int(route.duration / 60), route.distance / 1000]

    def crow_distance(origin, destination):
        origin_lat, origin_lon = origin[1], origin[0]
        destination_lat, destination_lon = destination[1], destination[0]
        return geopy.distance.geodesic((origin_lat, origin_lon), (destination_lat, destination_lon)).km

        stops = pd.read_csv(stops_input)
        stop_times = pd.read_csv(stop_times_input)
        stop_times_grouped = stop_times.groupby('trip_id')
        stop_times_ids = pd.concat([stop_times_grouped.nth(0)[['stop_id']], stop_times_grouped.nth(-1)[['stop_id']]])['stop_id'].drop_duplicates().tolist()
        stops = stops[stops.stop_id.isin(stop_times_ids)]
        lat_lon = stops[['stop_lat', 'stop_lon']].drop_duplicates()
        client = MapboxValhalla(api_key=api_key)
        coords = [[lon, lat] for lat, lon in lat_lon.values.tolist()]
        combinations = pd.DataFrame(
            [p for p in itertools.product(coords, repeat=2)])
        st.write('Do you want to use maximum and minimum distance threshold to reduce the size of the deadhead catalog (YES or NO):')

        agree = st.checkbox('YES')
        if agree:
            use_threshold = 'YES'
        else:
            use_threshold = 'NO'
        if use_threshold == 'YES':
            vec_crow_distance = np.vectorize(crow_distance)
            combinations['crow_distance'] = vec_crow_distance(combinations[0].values, combinations[1].values)
            max_threshold = float(st.number_input('Please enter the maximum distance threshold between 2 points you want to use (km):'))
            min_threshold = float(st.number_input('Please enter the minimum distance threshold between 2 points you want to use (km):'))
            combinations = combinations[(combinations.crow_distance < max_threshold) & (combinations.crow_distance > min_threshold) & (combinations[0] != combinations[1])]
        else:
            combinations = combinations[(combinations[0] != combinations[1])]
        combinations[['Origin Stop Id', 'Destination Stop Id', 'Travel Time', 'Distance']] = st.progress(
            lambda x: get_routing(x), axis=1, result_type='expand')
        columns = ['Start Time Range', 'End Time Range', '	Generate Time',	'Route Id'	, 'Origin Stop Name'	, 'Destination Stop Name',
                   'Days Of Week',	'Direction'	, 'Purpose'	, 'Alignment',	'Pre-Layover Time',	'Post-Layover Time',	'updatedAt']
        combinations = pd.concat([combinations, pd.DataFrame(columns=columns)])
        if use_threshold == 'YES':
            output = combinations.drop([0, 1, 'crow_distance'], axis=1).to_excel(
            'deadhead_catalog.xlsx', index=False, sheet_name='Deadheads')
            download = 1
        else:
            output = combinations.drop([0, 1], axis=1).to_excel(
            'deadhead_catalog.xlsx', index=False, sheet_name='Deadheads')
            download = 1

        with output as f:
            if download == 1:
                st.download_button(
                    label='Download the updated GTFS zip file',
                    data=f,
                    file_name='gtfs_updated.zip',
                    mime='application/zip'
                )

