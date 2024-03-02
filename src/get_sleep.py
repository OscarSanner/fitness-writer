from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


def get_sleep(date, google_auth_token):
    """
    Fetches sleep data for the specified date using the Google Fitness API and aggregates total sleep time.

    Parameters:
    - date (datetime.date): The date for which to fetch sleep data.
    - google_auth_token (str): Google authorization token.

    Returns:
    - float: Total sleep time in hours for the specified date.
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

    # Initialize total sleep time
    total_sleep_time_seconds = 0

    # Define the data source ID for sleep
    data_source = "derived:com.google.sleep.segment:com.google.android.gms:merge_sleep_segments"

    # Use the Fitness API to fetch sleep data
    dataset_id = f"{start_time_ns}-{end_time_ns}"
    data = service.users().dataSources().datasets().get(
        userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()

    # Iterate over the points to sum up the sleep time
    for point in data.get('point', []):
        start_time_point_ns = int(point['startTimeNanos'])
        end_time_point_ns = int(point['endTimeNanos'])
        sleep_duration_seconds = (end_time_point_ns - start_time_point_ns) / 1e9  # Convert nanoseconds to seconds
        total_sleep_time_seconds += sleep_duration_seconds

    # Convert total sleep time to hours
    total_sleep_time_hours = total_sleep_time_seconds / 3600

    return total_sleep_time_hours