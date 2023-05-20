import os
import json
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import streamlit as st



# Load environment variables


# Google OAuth2
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
scope = ["openid", "https://www.googleapis.com/auth/userinfo.email"]


def auth():
    # Define google_client_id, google_client_secret, and google_redirect_uri
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

    colx, coly, colz = st.columns([2,1,2])
    vert_space = '<div style="padding: 100px 0px;"></div>'
    # Create an empty placeholder for the vertical space

    if not authenticated:
        vert_space_placeholder = coly.empty()
        vert_space_placeholder.markdown(vert_space, unsafe_allow_html=True)  # Add the vertical space to the placeholder


    login_link_placeholder = coly.empty()
    
    font_awesome_placeholder = coly.empty()

    if not authenticated:
        google = OAuth2Session(google_client_id, scope=scope, redirect_uri=google_redirect_uri)
        authorization_url, state = google.authorization_url(authorization_base_url)

        font_awesome_cdn = """
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.0/css/all.min.css">
        """
        # Add the Google icon inside the <a> element
        google_icon = """
        <style>
            .google-login-btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
                padding: 10px 15px;
                background-color: #4285F4;
                border-radius: 4px;
                transition: background-color 0.2s;
            }}
            .google-login-btn:hover {{
                background-color: #246DC3;
            }}
        </style>
        <div style="display: flex; justify-content: center;">
            <a href="{authorization_url}" target="_self" class="google-login-btn" title="Login with Google">
                <i class="fab fa-google" style="font-size: 2rem; color: #FFFFFF;"></i>
            </a>
        </div>
        """.format(authorization_url=authorization_url)

        font_awesome_placeholder.markdown(font_awesome_cdn, unsafe_allow_html=True)
        login_link_placeholder.markdown(google_icon, unsafe_allow_html=True)
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
                    login_link_placeholder.empty()
                    vert_space_placeholder.empty() # Remove the login link
            except InvalidGrantError:
                pass  # Do nothing, effectively ignoring the error.

    if authenticated:
        font_awesome_placeholder.empty()
        return email
    else:
        return None


def get_user_email(token):
    response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + token)
    user_data = json.loads(response.text)
    return user_data.get('email')
    
