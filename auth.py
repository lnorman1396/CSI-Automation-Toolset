import os
import json
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Google OAuth2
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
scope = ["openid", "https://www.googleapis.com/auth/userinfo.email"]


def auth():
    
    # Check if user is authenticated
    authenticated = False
    token = st.session_state.get("token")
    email = None
    if token:
        email = get_user_email(token)
        if email:
            authenticated = True

    if not authenticated:
        google = OAuth2Session(st.secrets["google"]["client_id"], scope=scope, redirect_uri=st.secrets["google"]["redirect_uri"])
        authorization_url, state = google.authorization_url(authorization_base_url)

        # Display login link
        st.markdown(f'[Login with Google]({authorization_url})')

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
    
