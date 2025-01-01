import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from flask import Flask, request
import requests
import json
import time
import threading
import webbrowser
import os

PROJECT_ROOT = pathlib.Path(__file__).parent.resolve().parent.resolve()

# ---------------------------- GOOGLE ---------------------------- #

# Replace these with your client's information
GOOGLE_CLIENT_SECRET_FILE = os.path.join(PROJECT_ROOT, "auth_data", "google", "client_secret.json")
GOOGLE_TOKEN_PICKLE_FILE = os.path.join(PROJECT_ROOT, "auth_data", "google", "token.pickle")
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.activity.write',
    'https://www.googleapis.com/auth/fitness.blood_glucose.read',
    'https://www.googleapis.com/auth/fitness.blood_glucose.write',
    'https://www.googleapis.com/auth/fitness.blood_pressure.read',
    'https://www.googleapis.com/auth/fitness.blood_pressure.write',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.body.write',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.write',
    'https://www.googleapis.com/auth/fitness.body_temperature.read',
    'https://www.googleapis.com/auth/fitness.body_temperature.write',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.location.write',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    'https://www.googleapis.com/auth/fitness.nutrition.write',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.write',
    'https://www.googleapis.com/auth/fitness.reproductive_health.read',
    'https://www.googleapis.com/auth/fitness.reproductive_health.write',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.sleep.write',
    'https://www.googleapis.com/auth/spreadsheets'
]


def get_google_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(GOOGLE_TOKEN_PICKLE_FILE):
        with open(GOOGLE_TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid or os.getenv("ACQUIRE_TOKEN") == "true":
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRET_FILE, GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(GOOGLE_TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


# ---------------------------- STRAVA ---------------------------- #
app = Flask(__name__)

CONFIG_FILE = os.path.join(PROJECT_ROOT, "auth_data", "strava", "strava_config.json")
TOKEN_FILE = os.path.join(PROJECT_ROOT, "auth_data", "strava", "strava_tokens.json")
REDIRECT_URI = 'http://127.0.0.1:5000/exchange_token'


def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)


def exchange_token_for_credentials(code, client_id, client_secret):
    url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(url, data=payload)
    if response.ok:
        tokens = response.json()
        with open(TOKEN_FILE, 'w') as file:
            json.dump(tokens, file, indent=4)
        print("Strava tokens obtained and saved successfully.")
    else:
        print("Failed to exchange code for tokens.")


@app.route('/exchange_token')
def exchange_token():
    config = load_config()
    code = request.args.get('code')
    if code:
        exchange_token_for_credentials(code, config['client_id'], config['client_secret'])
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        return "You may close this window."
    else:
        return "No code provided."


def start_flask_server():
    app.run(port=5000)


def refresh_strava_tokens(client_id, client_secret, refresh_token):
    """Refresh the Strava access token using the refresh token."""
    refresh_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(refresh_url, data=payload)
    if response.ok:
        return response.json()  # Contains new access_token, refresh_token, and expires_at
    else:
        print("Failed to refresh Strava tokens:", response.text)
        return None


def get_lifesum_credentials():
    credentials_file_path = os.path.join(PROJECT_ROOT, "auth_data", "lifesum", "credentials.json")
    
    with open(credentials_file_path, 'r') as file:
        credentials = json.load(file)
    
    return {
        "base_api_url": credentials["base_api_url"],
        "password": credentials["password"],
        "username": credentials["username"]
    }

def get_strava_credentials():
    config = load_config()
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            tokens = json.load(file)

        # Check if the access token has expired
        if tokens.get('expires_at', 0) < time.time():
            print("Access token has expired. Refreshing tokens...")
            refreshed_tokens = refresh_strava_tokens(config['client_id'], config['client_secret'],
                                                     tokens['refresh_token'])
            if refreshed_tokens:
                # Update the token file with the new tokens
                with open(TOKEN_FILE, 'w') as file:
                    json.dump(refreshed_tokens, file, indent=4)
                print("Tokens refreshed successfully.")
                return refreshed_tokens
            else:
                print("Failed to refresh tokens.")
                return None
        else:
            return tokens
    else:
        threading.Thread(target=start_flask_server).start()
        auth_url = f"https://www.strava.com/oauth/authorize?client_id={config['client_id']}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=read,activity:read"
        webbrowser.open(auth_url)
        while not os.path.exists(TOKEN_FILE):
            pass
        with open(TOKEN_FILE, 'r') as file:
            tokens = json.load(file)
        return tokens
