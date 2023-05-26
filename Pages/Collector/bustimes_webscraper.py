from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import requests, datetime, io

class Description:
    title = "Timetable Scraper"
    icon = "https://play-lh.googleusercontent.com/KCsggSNENAaJL0fQI65iwclfIJ2bKm5G6p0dmKSVqbxZhrupfh2sx2msHUb_zYTv7JE"
    description = "This script scrapes the timetable of the current day for an operator of your choice."
    author = "Alex Long"

def run():

    done = False

    def get_operator_link(operator):
        driver.find_elements(By.NAME, 'q')[1].send_keys(operator)

        driver.find_elements(By.TAG_NAME, 'input')[3].click()

        operator_elements = driver.find_elements(By.TAG_NAME, 'a')

        operator_links = []
        for op in operator_elements:
            operator_link = op.get_attribute('href')
            operator_links.append(operator_link)

        correct_op_link = list(filter(lambda x: 'operators' in x, operator_links))

        operator_selects = st.selectbox(label = 'Returned operators:', options = correct_op_link)

        return operator_selects

    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

    driver.get('https://bustimes.org/')

    driver.find_element(By.CSS_SELECTOR, 'button.css-47sehv').click()

    st.warning('WARNING: Build in progress. (Contact alex if needed)')

    with st.form('Operator Form'):

        operator = st.text_input(label = 'Please type operator here:', placeholder = 'tlc')  # Input whatever operator you want, TODO idea would be to have this as a user input

        submit = st.form_submit_button(label = 'Submit')

        if submit:
            
            operator_selects = get_operator_link(operator)

            driver.get(operator_selects)

            elements = driver.find_elements(By.TAG_NAME, 'a')
            link = []
            for e in elements:
                route_link = e.get_attribute('href')
                link.append(route_link)
            correct_link = list(filter(lambda x: 'services' in x, link))

            route = 0
            df_dict = {}
            for cl in correct_link:
                driver.get(correct_link[route])
                table_present = driver.find_elements(By.CSS_SELECTOR, 'table')
                if table_present:  # TODO create table with stops (no times) OR service ID switch
                    dataframes = pd.read_html(correct_link[route])
                    df = 0
                    for dataframe in dataframes:
                        dataframe_route = dataframes[df]

                        for i, col in enumerate(dataframe_route.columns):
                            dataframe_route.rename(columns={col: f'trip_num_{i}'}, inplace=True)

                        direction = "Outbound" if df == 0 else "Inbound"

                        if len(dataframes) == 2:
                            route_title = driver.find_element(By.TAG_NAME, 'h1').text + ' - ' + direction
                        elif len(dataframes) > 2:
                            route_title = driver.find_element(By.TAG_NAME, 'h1').text + ' - ' + str(df)
                        else:
                            route_title = driver.find_element(By.TAG_NAME, 'h1').text

                        dataframe_route.rename(columns={'trip_num_0': route_title}, inplace=True)

                        response = requests.get(correct_link[route])
                        soup = BeautifulSoup(response.text, 'html.parser')
                        table = soup.find_all('table')[df]

                        links = []
                        for tr in table.find_all("tr"):
                            trs = tr.find_all("th")
                            for each in trs:
                                try:
                                    link = each.find('a')['href']
                                    if each.has_attr("rowspan"):
                                        if each["rowspan"] == "2":
                                            links.append(link)
                                            links.append(link)
                                    else:
                                        links.append(link)
                                except:  # TODO fix the bare except (it works so I don't really want to touch it)
                                    pass

                        df_stop_id = pd.DataFrame({'Stop_ID': links})
                        df_stop_id['Stop_ID'] = df_stop_id['Stop_ID'].str[7:]

                        timepoint = []
                        for tr in table.find_all("tr"):
                            row_class = tr.get('class')
                            if row_class is None:
                                tp = 1
                            else:
                                tp = 0
                            timepoint.append(tp)
                        df_timepoint = pd.DataFrame({'Timepoint': timepoint})

                        columns = dataframe_route.columns[1:]
                        columns = columns.tolist()

                        for col in columns:
                            if dataframe_route[col].dtypes == object:
                                dataframe_route[col] = dataframe_route[col].apply(lambda x: x.replace('s', '') if isinstance(x, str)
                                                                                else x)

                        delete_row = True
                        last_row = dataframe_route.iloc[dataframe_route.shape[0] - 1]
                        last_row_dict = last_row.to_dict()
                        for key, value in last_row_dict.items():
                            value = str(value)
                            if ':' in value:
                                delete_row = False
                        if delete_row:
                            dataframe_route = dataframe_route[:-1]

                        dataframe_route = dataframe_route.join(df_stop_id)
                        dataframe_route = dataframe_route.join(df_timepoint)
                        first_column = dataframe_route.pop('Timepoint')
                        dataframe_route.insert(0, 'Timepoint', first_column)
                        second_column = dataframe_route.pop('Stop_ID')
                        dataframe_route.insert(1, 'Stop_ID', second_column)

                        cols_with_hourly = dataframe_route.columns[dataframe_route.loc[1].astype(str).str.contains('hourly')]
                        
                        def get_consecutive_cols(cols_list):
                            consecutive_cols = []
                            temp = []
                            prev_index = -1
                            for col in cols_list:
                                if prev_index != -1 and dataframe_route.columns.get_loc(col) - prev_index != 1:
                                    consecutive_cols.append(temp)
                                    temp = []
                                temp.append(col)
                                prev_index = dataframe_route.columns.get_loc(col)
                            consecutive_cols.append(temp)
                            return consecutive_cols

                        consecutive_cols = get_consecutive_cols(cols_with_hourly)
                        
                        for group in consecutive_cols:
                            for col in group[1:]:
                                dataframe_route.drop(col, axis = 1, inplace = True)

                        cols_with_hourly = dataframe_route.columns[dataframe_route.loc[1].astype(str).str.contains('hourly')]

                        for col in cols_with_hourly:
                            col_index = dataframe_route.columns.get_loc(col)

                            left_col = col_index - 1
                            right_col = col_index + 1

                            valid_row = 0

                            while valid_row < dataframe_route.shape[0]:
                                current_row_value = dataframe_route.iloc[valid_row, left_col]
                                if type(current_row_value) == str:
                                    break
                                valid_row += 1

                            left_value = int(dataframe_route.iloc[valid_row, left_col][0:2])
                            right_value = int(dataframe_route.iloc[valid_row, right_col][0:2])

                            result = right_value - left_value - 1
                            for i in range(1, result):
                                dataframe_route.insert(col_index + i, f'Column {i}', 'hourly')

                        cols_to_iterate = dataframe_route.columns[3:]
                        for i, col_name in enumerate(cols_to_iterate):
                            for index, value in dataframe_route[col_name].iteritems():
                                if pd.isnull(value):
                                    continue
                                if ':' not in str(value):
                                    if 'hourly' in str(value):
                                        time_to_add = datetime.timedelta(hours = 1)
                                    elif '30' in str(value):
                                        time_to_add = datetime.timedelta(minutes = 30)
                                    elif '20' in str(value):
                                        time_to_add = datetime.timedelta(minutes = 20)
                                    elif '15' in str(value):
                                        time_to_add = datetime.timedelta(minutes = 15)
                                    elif '12' in str(value):
                                        time_to_add = datetime.timedelta(minutes = 12)
                                    else:
                                        print("Duration is not supported") # TODO implement a user input.
                                    prev_cell_value = dataframe_route.loc[index, cols_to_iterate[i - 1]]
                                    if pd.notnull(prev_cell_value):
                                        try:
                                            date_prev_cell = datetime.datetime.strptime(prev_cell_value, '%H:%M')
                                            new_cell_value = date_prev_cell + time_to_add
                                            new_cell_value = str(new_cell_value)
                                            new_cell_value = new_cell_value[11:16]
                                            dataframe_route.loc[index, col_name] = new_cell_value
                                        except:
                                            pass
                        
                        dataframe_route_T = dataframe_route.transpose()



                        # NOTE: We are creating a dictionary with keys - spreadsheet name, value - route dataframe
                        # this will be used later on to write the Excel. Might want to redesign it if you want both
                        # directions of one route in the same sheet. Name logic at the moment is "RX - Direction" e.g.
                        # R8 - Outbound
                        df_name = "R" + route_title.split("-")[0] + f"- {direction}"
                        df_dict[df_name] = dataframe_route_T

                        df = df + 1

                        # TODO stop catalogue, compare atco to excel, if blank create new sheet with northing eastings and compare with, and generate longs lats from https://gridreferencefinder.com/batchConvert/batchConvert.php

                route = route + 1

            # NOTE: This is a xlsxwriter that will loop through the df_dict and
            # write each route dataframe into a new sheet of the same workbook
            # Requires:
            #
            # - download xlsxwriter
            # - create a directory called "output" in your folder # NOTE: can remove this I did it to be tidy
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            for sht_name, route_df in df_dict.items():
                route_df.to_excel(writer, sheet_name=sht_name, index=False)
            writer.close()
            excel_data = output.getvalue()
            done = True
    if done:
        st.download_button(
            label="Download data as Excel",
            data=excel_data,
            file_name='route_output.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        driver.quit()
