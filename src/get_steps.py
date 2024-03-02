from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


def get_steps(date, google_auth_token):
    """
    Fetches the steps taken on the specified date using the Google Fitness API, ensuring that only
    data points that include mid_time are summed.

    Parameters:
    - date (datetime.date): The date for which to fetch steps.
    - google_auth_token (str): Google authorization token.

    Returns:
    - int: Number of steps taken on the specified date.
    """

    # Create credentials from the provided Google authorization token
    credentials = Credentials(token=google_auth_token)

    # Build the Fitness API service
    service = build('fitness', 'v1', credentials=credentials)

    # Define the time range for the query (whole day)
    timezone = pytz.timezone("Europe/Stockholm")  # Adjust to your timezone
    start_dt = datetime(date.year, date.month, date.day, tzinfo=timezone)
    end_dt = start_dt + timedelta(days=1)

    # Calculate mid time in nanoseconds
    mid_dt = start_dt + timedelta(hours=12)  # Midpoint of the day
    start_time_ns = int(start_dt.timestamp()) * 10**9
    end_time_ns = int(end_dt.timestamp()) * 10**9
    mid_time_ns = int(mid_dt.timestamp()) * 10**9

    # Define the data source ID for steps
    data_source = "raw:com.google.step_count.delta:com.sec.android.app.shealth:health_platform"

    # Use the Fitness API to fetch step count
    dataset_id = f"{start_time_ns}-{end_time_ns}"
    data = service.users().dataSources().datasets().get(
        userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()

    # Filter points and sum up the steps
    steps = 0
    for point in data.get('point', []):
        start_time_point_ns = int(point['startTimeNanos'])
        end_time_point_ns = int(point['endTimeNanos'])

        # Check if mid_time falls within the start and end time of the point
        if start_time_point_ns <= mid_time_ns <= end_time_point_ns:
            steps += sum(value['intVal'] for value in point.get('value', []) if 'intVal' in value)

    return steps