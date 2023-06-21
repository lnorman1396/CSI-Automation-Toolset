from custom_import_method import _import
#import streamlit as st

#ServiceAccountCredentials = _import('oauth2client.service_account.ServiceAccountCredentials')
st = _import('streamlit')
secrets = _import('secrets')

def run(full_name=None):

    def show_feedback_form(full_name):
        with st.form('Feedback form'):
            title = st.text_input(label='title')
            f_type = st.selectbox(label='feedback type', options= ['Bug', 'Product Gap', 'Script Idea', 'Other'])
            description = st.text_area(label='Description')
            priority = st.selectbox(label='Priority', options= ['Low', 'Medium', 'High', 'Urgent'])
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.success('Thanks for submitting your feedback, it has now been sent to the team for review')
                st.write(title)
                st.write(description)
                st.write(priority)
                st.write(full_name)