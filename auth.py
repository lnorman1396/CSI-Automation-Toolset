import os
import json
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import streamlit as st




# Google OAuth2
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
scope = ["openid", "https://www.googleapis.com/auth/userinfo.email"]


def auth():
   
    
    google_client_id = st.secrets["google"]["client_id"]
    google_client_secret = st.secrets["google"]["client_secret"]
    google_redirect_uri = st.secrets["google"]["redirect_uri"]
    
    # Check if user is authenticated
    authenticated = False
    token = st.session_state.get("token")
    email = None
    if token:
        email = get_user_email(token)
        if email:
            authenticated = True
            
    top_row_placeholder = st.empty()
    row_placeholder = st.empty()
    bottom_row_placeholder = st.empty()
            
    lt, top_space_placeholder, rt = top_row_placeholder.columns([1, 2, 1])
    left_column, login_card_placeholder, right_column = row_placeholder.columns([1, 2, 1])
    lb, bottom_space_placeholder, rb = bottom_row_placeholder.columns([1, 2, 1])

    if not authenticated:
        google = OAuth2Session(st.secrets["google"]["client_id"], scope=scope, redirect_uri=st.secrets["google"]["redirect_uri"])
        authorization_url, state = google.authorization_url(authorization_base_url)

        # Display login card
        
                # Display vertical space and login card
        top_space_placeholder.markdown("<div style='padding: 15vh 0px;'></div>", unsafe_allow_html=True)
        login_card = f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #fff;">
            <h6>Automation Toolset</h6>
            <p style="font-size: 0.8em; margin: 0; opacity: 0.7; font-style: italic; text-align: center;">You must have an Optibus email account to sign into this application</p>
            <a href="{authorization_url}" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #4285F4; color: #fff; text-decoration: none; border-radius: 5px;">Login with Google</a>
        </div>
        """
        login_card_placeholder.markdown(login_card, unsafe_allow_html=True)
        bottom_space_placeholder.markdown("<div style='padding: 20vh 0px;'></div>", unsafe_allow_html=True)
        
        


        code = st.experimental_get_query_params().get("code")

        if code:
            try:
                google.fetch_token(token_url, client_secret=google_client_secret, code=code[0])
                st.experimental_set_query_params(code=None)
                token = google.token["access_token"]
                st.session_state.token = token
                email = get_user_email(token)

                if email:
                    authenticated = True
                    # Clear the vertical space and login card
                    top_row_placeholder.empty()
                    
                    row_placeholder.empty()
                    bottom_row_placeholder.empty()
                    
                     
            except InvalidGrantError:
                pass  # Do nothing, effectively ignoring the error.

    if authenticated:
        return email  # Return the email if the user is authenticated
    else:
        return None

def get_user_email(token):
    response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + token)
    user_data = json.loads(response.text)
    return user_data.get('email')
    
