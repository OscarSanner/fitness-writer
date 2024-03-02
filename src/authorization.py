from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import requests
import json
from flask import Flask, request, redirect
import requests
import json
import threading
import webbrowser
import os

# ---------------------------- GOOGLE ---------------------------- #

# Replace these with your client's information
GOOGLE_CLIENT_SECRET_FILE = 'client_secret.json'
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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRET_FILE, GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

# ---------------------------- STRAVA ---------------------------- #
app = Flask(__name__)

CONFIG_FILE = 'strava_config.json'
TOKEN_FILE = 'strava_tokens.json'
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

def get_strava_credentials():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            tokens = json.load(file)
        return tokens
    else:
        threading.Thread(target=start_flask_server).start()
        config = load_config()
        auth_url = f"https://www.strava.com/oauth/authorize?client_id={config['client_id']}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=read,activity:read"
        webbrowser.open(auth_url)
        while not os.path.exists(TOKEN_FILE):
            pass
        with open(TOKEN_FILE, 'r') as file:
            tokens = json.load(file)
        return tokens
