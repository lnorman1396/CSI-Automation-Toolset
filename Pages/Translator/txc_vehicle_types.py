import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
from zipfile import ZipFile, ZIP_DEFLATED
import os

def run():
    def main():
      st.title("TXC File Processor")
      file = st.file_uploader("Upload TXC ZIP file", type="zip")
    
      if file is not None:
          with ZipFile(file, 'r') as zip:
              # Assuming there's only one XML file in the zip
              xml_file = [filename for filename in zip.namelist() if filename.endswith('.xml')][0]
              with zip.open(xml_file) as f:
                  content = f.read()
                  df = process_xml(content)
                  st.write(df)
    
                  # Write DataFrame to Excel and zip it
                  file_name = file.name[:-4]  # Strip file extension
                  output_bytes = write_output_TXC(df, file_name)
                  st.download_button(
                      label="Download output file",
                      data=output_bytes,
                      file_name='TXC_output.zip',
                      mime="application/zip"
                  )

    def process_xml(xml_content):
        df = pd.DataFrame(columns=["ServiceRef", "VehicleTypeCode"])
        context = ET.iterparse(io.BytesIO(xml_content), events=('end',))
        
        for event, elem in context:
            if elem.tag == '{http://www.transxchange.org.uk/}VehicleJourney':
                vehicle_type_code = elem.find('{http://www.transxchange.org.uk/}Operational/{http://www.transxchange.org.uk/}VehicleType/{http://www.transxchange.org.uk/}VehicleTypeCode')
                service_ref = elem.find('{http://www.transxchange.org.uk/}ServiceRef')
                
                if vehicle_type_code is not None and service_ref is not None:
                    df = df.append({
                        "ServiceRef": service_ref.text,
                        "VehicleTypeCode": vehicle_type_code.text,
                    }, ignore_index=True)
                elem.clear()
        return df

    def write_output_TXC(df, file_name):
        output_bytes = io.BytesIO()
        output_zip_file = ZipFile(output_bytes, 'w')
    
        # Write dataframe to Excel
        excel_file_name = file_name + '.xlsx'
        df.to_excel(excel_file_name, index=False, engine='openpyxl')
    
        # Add Excel file to zip
        output_zip_file.write(excel_file_name, compress_type=ZIP_DEFLATED)
    
        # Remove Excel file
        os.remove(excel_file_name)
    
        output_zip_file.close()
        output_bytes.seek(0)
        return output_bytes

    main()

