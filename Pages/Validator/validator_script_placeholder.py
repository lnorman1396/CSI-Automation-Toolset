import streamlit as st

class Description:
    title = "JDf to OGTFS Converter"
    description = "This is a script that converts a JDF zip file into OGTFS to enable you to import into optibus"
    icon = "https://cdn-icons-png.flaticon.com/512/1322/1322164.png"


def run():
    st.write('**TESTING Run Function**')
    st.caption('directories and files will only be presented in the UI if there is content to present. i.e if the Collector subdirectory is empty, it will not appear in the select page UI ')
