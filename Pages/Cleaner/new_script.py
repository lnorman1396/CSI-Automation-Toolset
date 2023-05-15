import streamlit as st
import pandas as pd
import xlsxwriter
import io

def run():
   def convert_csv_to_excel(csv_data):
        # Read the CSV data
        df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))

        # Perform your modifications here
        # df = ...

        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        excel_data = output.getvalue()

        return excel_data

    def main():
        st.title('CSV to Excel converter')

        uploaded_file = st.file_uploader('Upload CSV file', type='csv')
        if uploaded_file is not None:
            st.write('Uploaded file:')
            st.write(uploaded_file.name)

            # Convert the uploaded CSV to Excel
            excel_data = convert_csv_to_excel(uploaded_file.getvalue())

            # Generate a download link for the Excel file
            b64_excel = base64.b64encode(excel_data).decode()  # some strings
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" download="output.xlsx">Download Excel file</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write('Please upload a CSV file.')

   
