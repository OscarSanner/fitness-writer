from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


def get_weight(date, google_auth_token):
    """
    Fetches the latest weight measurement registered before the specified date using the Google Fitness API.

    Parameters:
    - date (datetime.date): The date to find the latest weight measurement before.
    - google_auth_token (str): Google authorization token.

    Returns:
    - float: The latest weight measurement before the specified date, or None if no data available.
    """

    # Create credentials from the provided Google authorization token
    credentials = Credentials(token=google_auth_token)

    # Build the Fitness API service
    service = build('fitness', 'v1', credentials=credentials)

    # Define a more recent start time for the query range, e.g., 5 years before the specified date
    start_dt = datetime(date.year - 5, 1, 1, tzinfo=pytz.timezone("Europe/Stockholm"))
    # Ensure end time is set to the beginning of the specified date
    end_dt = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Stockholm"))

    # Convert datetime to nanoseconds for the API
    start_time_ns = int(start_dt.timestamp()) * 10 ** 9
    # Adjust end_time_ns to be just before the specified date starts
    end_time_ns = int(end_dt.timestamp()) * 10 ** 9

    # Define the data source ID for weight
    data_source = "derived:com.google.weight:com.google.android.gms:merge_weight"

    # Use the Fitness API to fetch weight measurement
    dataset_id = f"{start_time_ns}-{end_time_ns}"
    data = service.users().dataSources().datasets().get(
        userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()

    # Filter for measurements and get the latest one before the specified date
    weight_measurements = [point for point in data.get('point', []) if point['endTimeNanos'] < str(end_time_ns)]
    if weight_measurements:
        # Sort by endTimeNanos to get the latest measurement
        latest_measurement = sorted(weight_measurements, key=lambda x: x['endTimeNanos'], reverse=True)[0]
        weight_value = latest_measurement['value'][0]['fpVal']  # Assuming weight is stored as floating-point value
        return weight_value

    return None  # Return None if no weight measurements are found before the specified date
