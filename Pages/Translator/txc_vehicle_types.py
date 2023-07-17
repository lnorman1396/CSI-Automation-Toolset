import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
from zipfile import ZipFile, ZIP_DEFLATED
import os

class Instructions:
    instructions = 'Upload the TXC File and run the script'
    
class Description:
    title = "Get Vehicle types and Routes from TXC"
    description = "The script reads TXC zip files and extracts routes and vehicle types to an excel"
    icon = "https://cdn-icons-png.flaticon.com/512/1869/1869397.png"
    author = 'Luke Norman'

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
        # Parse XML and find VehicleJourney elements
        root = ET.fromstring(xml_content)
        vehicle_journeys = root.findall('.//{http://www.transxchange.org.uk/}VehicleJourney')
    
        records = []
        for vj in vehicle_journeys:
            # Extract required elements
            vehicle_type_code = vj.find('{http://www.transxchange.org.uk/}Operational/{http://www.transxchange.org.uk/}VehicleType/{http://www.transxchange.org.uk/}VehicleTypeCode')
            service_ref = vj.find('{http://www.transxchange.org.uk/}ServiceRef')
    
            if vehicle_type_code is not None and service_ref is not None:
                records.append({
                    "ServiceRef": service_ref.text,
                    "VehicleTypeCode": vehicle_type_code.text,
                })
    
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(records)
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
