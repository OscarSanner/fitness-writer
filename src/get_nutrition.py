from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


def get_nutrition(date, google_auth_token):
    """
    Fetches nutrition information for the specified date using the Google Fitness API.

    Parameters:
    - date (datetime.date): The date for which to fetch nutrition information.
    - google_auth_token (str): Google authorization token.

    Returns:
    - dict: Nutrition information including kcal, protein, carbs, and fat.
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

    # Define the data source ID for nutrition
    data_source = "raw:com.google.nutrition:com.sillens.shapeupclub:health_platform"

    # Use the Fitness API to fetch nutrition data
    dataset_id = f"{start_time_ns}-{end_time_ns}"
    data = service.users().dataSources().datasets().get(
        userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()

    nutrition_totals = {
        'kcal': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0
    }

    # Iterate over the points to sum up the nutrition information
    for point in data.get('point', []):
        for value in point['value']:
            for nutrient_info in value.get('mapVal', []):
                key = nutrient_info['key']
                fpVal = nutrient_info['value'].get('fpVal', 0)

                if 'calories' in key:
                    nutrition_totals['kcal'] += fpVal
                elif 'protein' in key:
                    nutrition_totals['protein'] += fpVal
                elif 'carbs.total' in key:
                    nutrition_totals['carbs'] += fpVal
                elif 'fat.total' in key:
                    nutrition_totals['fat'] += fpVal

    return nutrition_totals

