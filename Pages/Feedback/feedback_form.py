from custom_import_method import _import
#import streamlit as st
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime

#ServiceAccountCredentials = _import('oauth2client.service_account.ServiceAccountCredentials')
st = _import('streamlit')
secrets = _import('secrets')





def generate_feedback_card(title, f_type, description, priority, full_name):
    type_color_map = {"Bug": "rgba(150, 0, 0, 0.6)", "Product Gap": "rgba(0, 68, 150, 0.6)", "Script Idea": "rgba(46, 87, 34, 0.6)", "Other": "rgba(255, 165, 0, 0.6)"}
    priority_color_map = {"Low": "rgba(46, 87, 34, 0.6)", "Medium": "rgba(123, 128, 65, 0.6)", "High": "rgba(150, 95, 0, 0.6)", "Urgent": "rgba(150, 0, 0, 0.6)"}
    
    type_color = type_color_map.get(f_type, "rgba(128, 128, 128, 0.6)") # Default color is grey if type is not in the map
    priority_color = priority_color_map.get(priority, "rgba(128, 128, 128, 0.6)") # Default color is grey if priority is not in the map
    full_name_color = "rgba(117, 6, 117, 0.6)" # Blue color for full name

    card = f"""
    <div style="border: 1px solid #ddd; border-radius: 10px; background-color: #f5f5f5; padding: 20px; margin-bottom: 10px; display: flex; flex-direction: column;">
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <img src="https://e1.pngegg.com/pngimages/418/839/png-clipart-macos-app-icons-feedback-assistant.png" style="width: 30px; height: 30px; margin-right: 10px;" alt="Icon">
            <h6 style="padding-top: 15px; align-self: center;">{title}</h6>
        </div>
        <hr style="border: none; height: 1px; background: #ddd; margin: 10px 0; width: 100%;">
        <div style="display: flex; justify-content: space-around; font-size: 0.8em; margin-bottom: 10px; margin-top: 10px; max-width: 80%; gap: 20px; margin-left: auto; margin-right: auto;">
            <p style="color: #fff; background-color: {type_color}; padding: 0px 10px; border-radius: 10px;">Type: {f_type}</p>
            <p style="color: #fff; background-color: {priority_color}; padding: 0px 10px; border-radius: 10px;">Priority: {priority}</p>
            <p style="color: #fff; background-color: {full_name_color}; padding: 0px 10px; border-radius: 10px;">Submitted by: {full_name}</p>
        </div>
        <p style="margin: 0; color: #000; background-color: #fff; padding: 10px 10px; border-radius: 10px; width: 100%; box-sizing: border-box;">Description: {description}</p>
    </div>
    """
    return card

def generate_feedback_cards(record):
    # Convert the 'date_reported' to the desired format
    date_reported_str = record['date_reported'].strftime('%H:%M %d-%m-%Y')

    # Define the icon maps
    type_icon_map = {
        'Bug': 'https://cdn.icon-icons.com/icons2/1808/PNG/512/bug_115148.png',
        'Script Idea': 'https://cdn-icons-png.flaticon.com/512/858/858113.png',
        'Product Gap': 'https://icon-library.com/images/products-icon-png/products-icon-png-9.jpg', 
        'Other':'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Blue_question_mark_icon.svg/2048px-Blue_question_mark_icon.svg.png'
    }

    priority_icon_map = {
        'Low': 'https://cdn-icons-png.flaticon.com/512/3696/3696670.png',
        'Medium': 'https://static-00.iconduck.com/assets.00/medium-priority-icon-512x512-kpm2vacr.png',
        'High': 'https://static-00.iconduck.com/assets.00/high-priority-icon-512x512-fk4ioedw.png',
        'Urgent': 'https://static.vecteezy.com/system/resources/previews/021/884/889/original/fluttering-two-pointed-end-flags-element-and-decoration-design-png.png'
    }

    # Get the appropriate icons
    type_icon = type_icon_map.get(record['type'], '')  # Default to empty string if type is not in the map
    priority_icon = priority_icon_map.get(record['priority'], '')  # Default to empty string if priority is not in the map

    card = f"""
    <div style="border: 1px solid #ddd; border-radius: 5px; background-color: #fff; padding: 10px; margin-bottom: 10px; display: grid; grid-template-columns: 1fr 100px 1fr;">
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <h6 style="margin: 0;">{record['title']}</h6>
            <p style="margin: 0 0 10px 0; color: #000;">{record['description']}</p>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px;">
            <img src="{type_icon}" style="width: 25px; height: 25px;" title="Type: {record['type']}">
            <img src="{priority_icon}" style="width: 25px; height: 25px;" title="Priority: {record['priority']}">
        </div>
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: flex-end;">
            <p style="margin: 0; font-size: 0.9em; color: #888;">{date_reported_str}</p>
            <p style="margin: 0; font-size: 0.8em;">Submitted by: {record['full_name']}</p>
        </div>
    </div>
    """
    return card












def run(full_name=None):
    uri = st.secrets['mongo']['uri']
    # Create a new client and connect to the server

    # Initialize connection.
    # Uses st.cache_resource to only run once.
    #@st.cache_resource
    client =  MongoClient(uri, server_api=ServerApi('1'))

    # Database Name
    db = client["automationtoolset"]
    
    # Collection Name
    col = db["feedbackreport"]
    

    form, feedback = st.tabs(['Feedback Form', 'Logged Feedback'])
    
    def show_feedback_form(full_name):
        with st.form('Feedback form'):
            title = st.text_input(label='title')
            f_type = st.selectbox(label='feedback type', options= ['Bug', 'Product Gap', 'Script Idea', 'Other'])
            description = st.text_area(label='Description')
            priority = st.selectbox(label='Priority', options= ['Low', 'Medium', 'High', 'Urgent'])
            submitted = st.form_submit_button("Submit")
            if submitted:
                if description != '' and title !='':
                    st.success('Thanks for submitting your feedback, it has now been sent to the team for review')
                    feedback_card = generate_feedback_card(title, f_type, description, priority, full_name)
                    st.markdown(feedback_card, unsafe_allow_html=True)
                    # Create a dictionary
                    data = {
                        'title': title,
                        'type': f_type,
                        'description': description,
                        'priority': priority,
                        'full_name': full_name,
                        'date_reported': datetime.datetime.now()
                    }
                    Post_record_to_mongo = col.insert_one(data)
                else:
                    st.warning('Description and title must be not be blank')

    with form: 
        show_feedback_form(full_name)
    with feedback:
        col1, col2 = st.columns([7,2])
        col1.info('View Feedback Requests')
        _filter = col2.selectbox(label='filter', options= ['Only Me', 'All'], label_visibility='collapsed', help='View Filter')
        if _filter == 'Only Me':

            records = col.find({"full_name": full_name})
        else: 
            records = col.find()

        for record in records:
            feedback_card_preview = generate_feedback_cards(record)
            st.markdown(feedback_card_preview, unsafe_allow_html=True)
