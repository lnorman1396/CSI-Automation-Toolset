import streamlit as st
import os
import zipfile
import os
import tempfile
import traceback
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
import pandas as pd
from routingpy.routers import MapboxValhalla
import itertools
import geopy.distance
import csv
import io
import openpyxl


logger = st.expander('Logger for debugging')

class Instructions:
    instructions = 'Upload the VDV452 File and run the scripts to perform different Actions for VDV452'
    link = 'tbd'

class Description:
    title = "VDV452 - Toolset"
    description = "This is a toolset which enables you to run different common practises on VDV 452"
    icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Verband_Deutscher_Verkehrsunternehmen_Logo.svg/1200px-Verband_Deutscher_Verkehrsunternehmen_Logo.svg.png"
    author = 'Janco Loenneker'


def run():


    st.title('VDV Tools v0.3')
    st.caption('You can use this tools to check and edit VDV452 Files. Please note, that the VDV452 file must be directly compressed. If there is an extra folder in the .zip Archive it will fail and not find the files.')
    uploaded_file = st.file_uploader('Upload a VDV zip file:', type=['zip'])

    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_path = 'temp.zip'
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Let users select a function to perform
        function_options = ['Switch Columns', 'Add New Vehicle', 'Update Coordinates', 'Check VDV Files', 'Show Start/End Stops on Map', 'Create Deadhead Catalog']
        selected_function = st.selectbox('Select a function to perform:', function_options)

        if selected_function == 'Add New Vehicle':
            new_id = st.text_input('Enter the new vehicle ID:', '')
        elif selected_function == 'Create Deadhead Catalog':
            ort_nr = st.text_input('Enter ORT_NR:')
            coordinates = st.text_area('Enter coordinates (comma-separated):')

        # Process the file with the selected function
        process_button = st.button('Process VDV zip file')
        if process_button:
            try:
                download = 1
                if selected_function == 'Switch Columns':
                    new_zip_path = switch_ort_names(temp_path)
                    print(new_zip_path)

                elif selected_function == 'Add New Vehicle':
                    temp_dir = 'temp_folder'

                    new_zip_path = update_zip(temp_path, new_id, 1)
                    print(new_zip_path)

                elif selected_function == 'Check VDV Files':
                    temp_dir = 'temp_folder'

                    check1 = update_zip(temp_path, 0, 4)
                    check2 = update_zip(temp_path, 0, 5)
                    check3 = update_zip(temp_path, 0, 6)
                    check4 = update_zip(temp_path, 0, 7)
                    check5 = update_zip(temp_path, 0, 3)
                    st.write("Empty Files found: ", check1)
                    st.write("Additional Files found: ", check2)
                    st.write(check3)
                    st.write(check4)
                    st.write(check5)
                    st.success("VDV Check finished")
                    new_zip_path = temp_path
                    download = 0

                elif selected_function == 'Check for additional Files':
                    temp_dir = 'temp_folder'

                    check = update_zip(temp_path, 0, 5)
                    st.success(check)
                    new_zip_path = temp_path
                    download = 0

                elif selected_function == 'Validate Files':
                    temp_dir = 'temp_folder'

                    check = update_zip(temp_path, 0, 6)
                    st.success(check)
                    new_zip_path = temp_path
                    download = 0

                elif selected_function == 'Check for Columns with 0s':
                    temp_dir = 'temp_folder'

                    check = update_zip(temp_path, 0, 7)
                    st.success(check)
                    new_zip_path = temp_path
                    download = 0

                elif selected_function == 'Check for empy Coordinates':
                    temp_dir = 'temp_folder'

                    check = update_zip(temp_path, 0, 3)
                    st.success(check)
                    new_zip_path = temp_path
                    download = 0
                elif selected_function == 'Update Coordinates':

                    new_zip_path = update_zip(temp_path, 0, 2)
                    print(new_zip_path)
                    st.success(f'VDV452 zip file updated successfully: {new_zip_path}')

                elif selected_function == 'Show Start/End Stops on Map':
                    download = 0
                    stops = view_stops_on_map(temp_path)
                    st.header('Start/End Stops: ')
                    st.map(stops)
                    new_zip_path = temp_path

                elif selected_function == 'Create Deadhead Catalog':
                    custom_stop_coordinates = []
                    if ort_nr and coordinates:
                        # Parse coordinates string into a list
                        coordinates = [float(coord) for coord in coordinates.split(',')]
                        # Add the custom ORT_NR and coordinates to the coordinates list
                        custom_stop_coordinates.append((coordinates, ort_nr))

                    excel_data = create_deadhead_catalog(temp_path, custom_stop_coordinates)

                    st.success(f'Deadhead Catalog finished:')
                    st.download_button(
                        label='Download Deadhead Catalog',
                        data=excel_data,
                        file_name='deadhead.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    new_zip_path = temp_path
                # Offer the processed file for download
                with open(new_zip_path, 'rb') as f:
                    if download == 1:
                        st.download_button(
                            label='Download the updated VDV zip file',
                            data=f,
                            file_name='vdv_updated.zip',
                            mime='application/zip'
                        )


                # Remove the temporary files
                os.remove(new_zip_path)
            except Exception as e:
                st.error(f'Error processing the VDV zip file: {str(e)}')

    encoding = "iso-8859-1"

def extract_vdv452_zip(zip_path, tempdir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tempdir)

def check_zero_columns(zip_path, files_to_check):
    zero_columns = {}

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in files_to_check:
            if file_name not in zip_ref.namelist():
                continue

            with zip_ref.open(file_name) as file:
                file_content = file.read().decode('iso-8859-1')
                lines = file_content.splitlines()

                columns = None
                column_values = {}

                for line in lines:
                    if line.startswith("atr;"):
                        columns = [col.strip() for col in line.split(";")[1:]]
                        for column in columns:
                            column_values[column] = []

                    if line.startswith("rec;"):
                        values = line.split(";")[1:]
                        for column, value in zip(columns, values):
                            column_values[column].append(value)

                if columns is None:
                    continue

                for column, values in column_values.items():
                    if all(value == '0' or value == '' for value in values):
                        if file_name not in zero_columns:
                            zero_columns[file_name] = []
                        zero_columns[file_name].append(column)

    result = "Columns containing only zeros:\n"
    for file_name, columns in zero_columns.items():
        result += f"{file_name}: {', '.join(columns)}\n"

    return result.strip()

def validate_files(zip_path):
    required_columns = {
        "rec_frt.x10": [
            "FRT_FID", "LI_NR", "STR_LI_VAR", "TAGESART_NR", "FAHRTART_NR", "FZG_TYP_NR",
            "FGR_NR", "FRT_START", "UM_UID"
        ],
        "lid_verlauf.x10": [
            "LI_NR", "STR_LI_VAR", "LI_LFD_NR", "ORT_NR", "ONR_TYP_NR"
        ],
        # Add the remaining required columns for the other files
    }

    optional_files = {
        "rec_umlauf.x10", "firmenkalender.x10"
    }

    missing_columns = {}
    missing_files_list = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        files_to_check = set(required_columns.keys()) | optional_files
        files_found = set(zip_ref.namelist())
        print(files_found)
        missing_files = files_to_check - files_found
        if missing_files:
            missing_files_list.append(f"Missing files: {', '.join(missing_files)}")

        for file_name, columns in required_columns.items():
            if file_name not in files_found:
                continue

            with zip_ref.open(file_name) as file:
                file_content = file.read().decode('iso-8859-1')
                lines = file_content.splitlines()

                for line in lines:
                    if line.startswith("atr;"):
                        present_columns = [col.strip() for col in line.split(";")[1:]]
                        break
                else:
                    missing_files_list.append(f"File {file_name} does not contain an 'atr;' line.")
                    continue

                missing_columns[file_name] = [column for column in columns if column not in present_columns]

    missing_columns_list = [
        f"{file_name}: {', '.join(columns)}"
        for file_name, columns in missing_columns.items() if columns
    ]

    result = ""
    if missing_files_list:
        result += "\n".join(missing_files_list) + "\n"
        print(missing_files_list)
        print(1)
        print(result)

    if missing_columns_list:
        result += "The following columns are missing:\n"
        result += "\n".join(missing_columns_list)
        print(missing_columns_list)
        print(2)
        print(result)
    if not result:
        result = "All required files and columns are present."

    return result


def get_stop_coordinates(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open('rec_ort.x10') as rec_ort_file, zip_ref.open('lid_verlauf.x10') as lid_verlauf_file:
            rec_ort_reader = csv.reader((line.decode('iso-8859-1').replace('\0', '') for line in rec_ort_file), delimiter=';')
            lid_verlauf_reader = csv.reader((line.decode('iso-8859-1').replace('\0', '') for line in lid_verlauf_file), delimiter=';')

            rec_ort_headers = next(row for row in rec_ort_reader if row[0].strip() == 'atr')
            lid_verlauf_headers = next(row for row in lid_verlauf_reader if row[0].strip() == 'atr')

            rec_ort_headers = [header.strip() for header in rec_ort_headers]
            lid_verlauf_headers = [header.strip() for header in lid_verlauf_headers]

            st.write("rec_ort_headers finished")
            st.write("lid_verlauf_headers finished")

            rec_ort_ort_nr_idx = rec_ort_headers.index('ORT_NR')
            rec_ort_coords_idx = (rec_ort_headers.index('ORT_POS_BREITE'), rec_ort_headers.index('ORT_POS_LAENGE'))
            lid_verlauf_ort_nr_idx = lid_verlauf_headers.index('ORT_NR')
            lid_verlauf_str_li_var_idx = lid_verlauf_headers.index('STR_LI_VAR')
            lid_verlauf_li_nr_idx = lid_verlauf_headers.index('LI_NR')
            lid_verlauf_li_lfd_nr_idx = lid_verlauf_headers.index('LI_LFD_NR')

            rec_ort_data = {row[rec_ort_ort_nr_idx]: (row[rec_ort_coords_idx[0]], row[rec_ort_coords_idx[1]], row[rec_ort_ort_nr_idx]) for row in rec_ort_reader if row[0].strip() == 'rec'}
            lid_verlauf_data = {(row[lid_verlauf_str_li_var_idx], row[lid_verlauf_li_nr_idx]): (row[lid_verlauf_ort_nr_idx], row[lid_verlauf_li_lfd_nr_idx]) for row in lid_verlauf_reader if row[0].strip() == 'rec'}

            # Group by STR_LI_VAR and LI_NR, and get the ORT_NR for the min and max LI_LFD_NR in each group
            lid_verlauf_data = pd.DataFrame(lid_verlauf_data.items(), columns=['Route', 'Data'])
            lid_verlauf_data[['ORT_NR', 'LI_LFD_NR']] = pd.DataFrame(lid_verlauf_data['Data'].tolist(), index=lid_verlauf_data.index)
            lid_verlauf_data['LI_LFD_NR'] = lid_verlauf_data['LI_LFD_NR'].astype(int)
            start_end_stops = lid_verlauf_data.groupby('Route')['ORT_NR'].agg(['first', 'last'])

            common_stop_coordinates = [rec_ort_data[ort_nr] for ort_nr in start_end_stops.values.flatten() if ort_nr in rec_ort_data]
            st.write(common_stop_coordinates)
            return common_stop_coordinates






def get_routing(row, client):
    origin, destination = row[0], row[1]
    origin_ort, destination_ort = origin[2], destination[2]
    route = client.directions(locations=[(origin[1],origin[0]), (destination[1],destination[0])], profile='bus')
    return [origin_ort,destination_ort,(route.duration / 60), route.distance / 1000]


def create_deadhead_catalog(zip_path, custom_stop_coordinates=None):
    api_key = 'pk.eyJ1IjoiemFjaGFyaWVjaGViYW5jZSIsImEiOiJja3FodjU3d2gwMGdoMnhxM2ZmNjZkYXc5In0.CSFfUFU-zyK_K-wwYGyQ0g'
    stops_coordinates = get_stop_coordinates(zip_path)
    st.write('Stop Coordinates finished')
    if custom_stop_coordinates:
        stops_coordinates.extend(custom_stop_coordinates)

    lat_lon = pd.DataFrame(stops_coordinates, columns=['ORT_POS_LAENGE', 'ORT_POS_BREITE', 'ORT_NR']).drop_duplicates()
    lat_lon['ORT_POS_BREITE'] = lat_lon['ORT_POS_BREITE'].apply(lambda x: x[:2] + '.' + x[2:])
    lat_lon['ORT_POS_LAENGE'] = lat_lon['ORT_POS_LAENGE'].apply(lambda x: x[:2] + '.' + x[2:])


    client = MapboxValhalla(api_key=api_key)

    coords = [[lat, lon, ort_nr] for lat, lon, ort_nr in lat_lon.values.tolist()]
    combinations = pd.DataFrame([p for p in itertools.product(coords, repeat=2)])
    combinations = combinations[combinations[0] != combinations[1]]  # Exclude pairs with the same coordinates
    combinations = combinations.apply(lambda x: tuple(sorted([tuple(x[0]), tuple(x[1])])), axis=1)  # Sort pairs and convert to tuple
    combinations = pd.DataFrame(combinations.tolist()).drop_duplicates()  # Remove duplicates

    results = []

    st.write("Progress")
    progress_bar = st.progress(0)
    total_combinations = len(combinations)

    for i, row in combinations.iterrows():
        try:
            result = get_routing(row, client)
        except Exception as e:
            pass
        results.append(result)

        # Update the progress bar
        try:
            progress_bar.progress((i + 1) / (total_combinations + 1))

        except Exception as e:
            pass

    results_df = pd.DataFrame(results, columns=['Origin Stop Id', 'Destination Stop Id', 'Travel Time', 'Distance'])

    columns = ['Start Time Range', 'End Time Range', 'Generate Time', 'Route Id', 'Origin Stop Name',
               'Destination Stop Name',
               'Days Of Week', 'Direction', 'Purpose', 'Alignment', 'Pre-Layover Time', 'Post-Layover Time',
               'updatedAt']

    combinations = pd.concat([results_df, pd.DataFrame(columns=columns)])


    # Write DataFrame to BytesIO object
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        combinations.to_excel(writer, index=False, sheet_name='Deadheads')

    # Retrieve the BytesIO object's content
    excel_data = output.getvalue()

    return excel_data


def view_stops_on_map(zip_path):
    stops_coordinates = get_stop_coordinates(zip_path)
    lat_lon = pd.DataFrame(stops_coordinates, columns=['lat', 'lon', 'ORT_NR']).drop_duplicates()
    lat_lon.drop(['ORT_NR'], axis=1)
    lat_lon['lat'] = lat_lon['lat'].apply(lambda x: x[:2] + '.' + x[2:]).astype(float)
    lat_lon['lon'] = lat_lon['lon'].apply(lambda x: x[:2] + '.' + x[2:]).astype(float)
    return lat_lon


def update_coordinates(content):
    updated_content = []
    header_row = None

    for line in content:
        if not header_row and line.startswith("atr;"):
            header_row = line.split(";")
            try:
                ort_pos_breite_index = header_row.index("ORT_POS_BREITE")
                ort_pos_hoehe_index = header_row.index("ORT_POS_LAENGE")
                print(ort_pos_hoehe_index)
            except ValueError:
                print("Error: ORT_POS_BREITE or ORT_POS_LAENGE not found in the header row.")
                return content
            updated_content.append(line)

        elif line.startswith("rec;"):
            columns = line.split(";")
            if len(columns) > max(ort_pos_breite_index, ort_pos_hoehe_index):
                columns[ort_pos_breite_index] = columns[ort_pos_breite_index] + "0"
                columns[ort_pos_hoehe_index] = columns[ort_pos_hoehe_index] + "0"
                updated_line = ";".join(columns)
                updated_content.append(updated_line)
            else:
                print(f"Warning: Line has fewer columns than expected - {line}")
                updated_content.append(line)
        else:
            updated_content.append(line)
    return updated_content

def update_zip(zip_path, new_id,selector):
    with tempfile.TemporaryDirectory() as tempdir:
        extract_vdv452_zip(zip_path, tempdir)
        if selector == 1:
            menge_fzg_typ_path = os.path.join(tempdir, 'menge_fzg_typ.x10')
            content = readlines_from_file(menge_fzg_typ_path)
            updated_content = add_new_line(content, new_id)
            write_file(menge_fzg_typ_path, updated_content)

        if selector == 2:
            rec_ort_path = os.path.join(tempdir, 'rec_ort.x10')
            rec_ort_content = readlines_from_file(rec_ort_path)
            updated_rec_ort_content = update_coordinates(rec_ort_content)
            write_file(rec_ort_path, updated_rec_ort_content)
        if selector ==3:
            rec_ort_path = os.path.join(tempdir, 'rec_ort.x10')
            empty_coordinates = check_empty_coordinates(rec_ort_path)
            if empty_coordinates:
                print("Empty coordinates found at the following line numbers:")
                print(empty_coordinates)
            else:
                print("No empty coordinates found.")
                empty_coordinates = 'No empty Coordinates'
            return empty_coordinates
        if selector ==4:
            files_without_rec = find_files_without_rec(zip_path)
            if files_without_rec:
                print(files_without_rec)
            else:
                files_without_rec = "All files have lines starting with 'rec;'."
            return files_without_rec
        if selector ==5:
            additional_files_with_rec = find_additional_files_with_rec(zip_path)
            if additional_files_with_rec:
                print(additional_files_with_rec)
            else:
                additional_files_with_rec = "No additional files"
            return additional_files_with_rec
        if selector ==6:
            validation_result = validate_files(zip_path)

            if validation_result:
                print("The files are valid.")
            else:
                print("The files are not valid.")
            return validation_result
        if selector ==7:
            files_to_check = ["rec_frt.x10", "lid_verlauf.x10", "rec_lid.x10"]
            zero_columns = check_zero_columns(zip_path, files_to_check)
            return zero_columns

        if selector ==8:
            switch = switch_ort_names(zip_path)
            print(switch)

        new_zip = save_updated_vdv452_zip(zip_path, tempdir)
        return new_zip

def readlines_from_file(file_path):
    with open(file_path, 'r', encoding=encoding) as file:
        content = file.readlines()
    return content

def write_file(file_path, content):
    with open(file_path, 'w', encoding=encoding) as file:
        file.writelines(content)

def add_new_line(content, new_id):
    new_line = f"rec;1000;{new_id};0;0;0;\"New Bus {new_id}\";0;\"NB{new_id}\""
    for index, line in enumerate(content):
        if line.startswith("end;"):
            content.insert(index, new_line)
            break
    return content

def save_updated_vdv452_zip(zip_path, tempdir):
    with zipfile.ZipFile(zip_path, 'w') as zip_ref:
        for foldername, subfolders, filenames in os.walk(tempdir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zip_ref.write(file_path, os.path.relpath(file_path, tempdir))
    return zip_path

def check_empty_coordinates(file_path):
    empty_coordinates = []
    header_row = None
    ort_pos_breite_index = None
    ort_pos_hoehe_index = None

    with open(file_path, 'r', encoding='iso-8859-1') as file:
        lines = file.readlines()

    for index, line in enumerate(lines, start=1):
        if not header_row and line.startswith("chs;"):
            header_row = line.split(";")
            try:
                ort_pos_breite_index = header_row.index("ORT_POS_BREITE")
                ort_pos_hoehe_index = header_row.index("ORT_POS_HOEHE")
            except ValueError:
                print("Error: ORT_POS_BREITE or ORT_POS_HOEHE not found in the header row.")
                return empty_coordinates

        elif line.startswith("rec;"):
            columns = line.split(";")
            if len(columns) > max(ort_pos_breite_index, ort_pos_hoehe_index):
                if not columns[ort_pos_breite_index] or not columns[ort_pos_hoehe_index]:
                    empty_coordinates.append(index)
            else:
                print(f"Warning: Line has fewer columns than expected - {line}")

    return empty_coordinates

def find_files_without_rec(zip_path):
    files_without_rec = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            with zip_ref.open(file_name) as file:
                file_content = file.read().decode('iso-8859-1')
                if not any(line.startswith("rec;") for line in file_content.splitlines()):
                    files_without_rec.append(file_name)

    return files_without_rec
def find_additional_files_with_rec(zip_path):
    predefined_files = {
        'menge_fzg_typ.x10',
        'rec_umlauf.x10',
        'menge_fahrtart.x10',
        'rec_frt.x10',
        'sel_fzt_feld.x10',
        'menge_fgr.x10',
        'rec_znr.x10',
        'lid_verlauf.x10',
        'rec_sel.x10',
        'rec_ort.x10',
        'menge_ort_typ.x10',
        'menge_onr_typ.x10',
        'menge_bereich.x10',
        'rec_lid.x10',
        'menge_tagesart.x10',
        'basis_ver_gueltigkeit.x10',
        'menge_basis_versionen.x10',
    }

    additional_files_with_rec = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower() not in predefined_files:
                with zip_ref.open(file_name) as file:
                    file_content = file.read().decode('iso-8859-1')
                    if any(line.startswith("rec;") for line in file_content.splitlines()):
                        additional_files_with_rec.append(file_name)

    return additional_files_with_rec




def switch_ort_names(zip_path):
    temp_dir = 'temp_folder'

    # Extract zip file contents to a temporary folder
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    encoding='iso-8859-1'

    # Read the content of rec_ort.x10 to find the encoding
    with open(os.path.join(temp_dir, 'rec_ort.x10'), 'r', encoding=encoding) as file:
        for line in file:
            if line.startswith("chs;"):
                encoding = line.strip().split(";")[1]
                break

    # Read the content of rec_ort.x10 using the detected encoding
    with open(os.path.join(temp_dir, 'rec_ort.x10'), 'r', encoding=encoding) as file:
        content = file.readlines()

    # Find and switch column headers
    for index, line in enumerate(content):
        if line.startswith("atr;"):
            columns = [col.strip() for col in line.split(";")]
            try:
                ort_name_index = columns.index('ORT_NAME')
                ort_ref_ort_name_index = columns.index('ORT_REF_ORT_NAME')
                columns[ort_name_index], columns[ort_ref_ort_name_index] = columns[ort_ref_ort_name_index], columns[
                    ort_name_index]
                content[index] = ";".join(columns)
                break
            except ValueError:
                raise ValueError("Column headers not found in rec_ort.x10")

    # Save the updated rec_ort.x10 using the detected encoding
    with open(os.path.join(temp_dir, 'rec_ort.x10'), 'w', encoding=encoding) as file:
        file.writelines(content)

    # Create a new zip file with the updated content
    new_zip_path = os.path.splitext(zip_path)[0] + '_updated.zip'
    with ZipFile(new_zip_path, 'w', compression=ZIP_DEFLATED) as new_zip:
        for folder_name, subfolders, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                new_zip.write(file_path, os.path.relpath(file_path, temp_dir))

    # Remove the temporary folder
    shutil.rmtree(temp_dir)

    return new_zip_path

