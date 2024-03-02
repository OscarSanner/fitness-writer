from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

def get_resting_heart_rate(date, google_auth_token):
    """
    Fetches the resting heart rate for the specified date using the Google Fitness API.

    Parameters:
    - date (datetime.date): The date for which to fetch the resting heart rate.
    - google_auth_token (str): Google authorization token.

    Returns:
    - float: Resting heart rate for the specified date, or None if no data available.
    """

    # Create credentials from the provided Google authorization token
    credentials = Credentials(token=google_auth_token)

    # Build the Fitness API service
    service = build('fitness', 'v1', credentials=credentials)

    # Define the time range for the query (whole day)
    timezone = pytz.timezone("Europe/Stockholm")  # Adjust to your timezone
    start_dt = datetime(date.year, date.month, date.day, tzinfo=timezone)
    end_dt = start_dt + timedelta(days=1)

    # Convert datetime to nanoseconds for the API
    start_time_ns = int(start_dt.timestamp()) * 10 ** 9
    end_time_ns = int(end_dt.timestamp()) * 10 ** 9

    # Define the data source ID for resting heart rate
    data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm"

    # Use the Fitness API to fetch resting heart rate data
    dataset_id = f"{start_time_ns}-{end_time_ns}"
    data = service.users().dataSources().datasets().get(
        userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()

    # Assuming there might be multiple measurements, select the minimum as resting
    heart_rates = [point['value'][0]['fpVal'] for point in data.get('point', []) if 'fpVal' in point['value'][0]]
    if heart_rates:
        return min(heart_rates)  # Assuming resting heart rate is the lowest measured value

    return None  # Return None if no resting heart rate data is found
