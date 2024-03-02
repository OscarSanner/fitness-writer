from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def list_data_sources(google_auth_token):
    """
    Lists all data sources available through the Google Fitness API for the authenticated user.

    Parameters:
    - google_auth_token (str): Google OAuth2 access token.

    Returns:
    - List of data sources.
    """
    # Create credentials from the provided Google OAuth2 access token
    credentials = Credentials(token=google_auth_token)

    # Build the Fitness API service
    service = build('fitness', 'v1', credentials=credentials)

    # Use the Fitness API to fetch available data sources
    data_sources_list = service.users().dataSources().list(userId='me').execute()

    # Extract and return the list of data sources
    data_sources = data_sources_list.get('dataSource', [])
    return data_sources

