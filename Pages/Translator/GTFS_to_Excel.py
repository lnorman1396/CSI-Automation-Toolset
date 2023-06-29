import streamlit as st
import pandas as pd
import os
import time
from zipfile import ZipFile
from io import BytesIO

class Instructions:
    instructions = 'Upload the Zip GTFS File and run the script to download a converted Excel file, for more info click on the Confluence link'
    link = 'https://optibus.atlassian.net/wiki/spaces/OP/pages/2123595829/GTFS+Scripts'


class Description:
    title = "GTFS to Excel"
    description = "This is a script that converts a GTFS zip file into an excel file"
    icon = "data:image/jpeg;base64,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"
    author = "Eytan Gross"

def run():
    
    logger = st.expander('logging outputs for debugging')
    def main():
       

        uploaded_file = st.file_uploader("Select GTFS zip file", type=['zip'])
        if uploaded_file is not None:
            start_time = time.time()
            logger.write('Reading GTFS file')
            zip_file_input = ZipFile(uploaded_file, 'r')
            output_name = uploaded_file.name[:-4]
            gtfs = get_gtfs(zip_file_input, output_name)
            logger.write(f'\nRead GTFS in {(time.time() - start_time):.1f} seconds')
            output = write_excel(gtfs, output_name + '.xlsx')
            logger.write(f'\nScript ran in {(time.time() - start_time):.1f} seconds')
            st.download_button("Download Excel File", output, output_name + '.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def get_gtfs(zip_file_input, output_name):
        df = pd.DataFrame(zip_file_input.namelist(), columns=['file_name'])
        df['extension'] = df['file_name'].str.split('.').str[-1].str.lower()
        df = df[df['extension'] == 'txt'].reset_index(drop=True)
        df['file_type'] = df['file_name'].str.split('.').str[0]
        gtfs = {}
        for index, row in df.iterrows():
            if zip_file_input.getinfo(row['file_name']).file_size > 0:
                logger.write(f'Reading {row["file_type"]} file')
                table = pd.read_csv(zip_file_input.open(row['file_name']), header=0, dtype=str)
                if len(table) > 1048574:
                    logger.write(f'{row["file_name"]} file has {len(table)} rows and will be saved as a csv file')
                    table.to_csv(f'{output_name}_{row["file_type"]}.csv')
                else:
                    logger.write(f'{row["file_type"]} file has {len(table)} rows')
                    gtfs[row['file_type']] = table
            else:
                logger.write(row['file_type'] + ' file has 0 rows')
                gtfs[row['file_type']] = pd.DataFrame()
        return(gtfs)

    def write_excel(table_array, output_name):
        start_time = time.time()
        logger.write('\nWriting excel output')
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for i in table_array:
                table_array[i].to_excel(writer, sheet_name=i)
        logger.write(f'Wrote excel output in {(time.time() - start_time):.1f} seconds')
        output.seek(0)
        return output.getvalue()

    main()
