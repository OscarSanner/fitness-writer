from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz


def print_datapoints_for_date(credentials, date):
    # Convert the date to the required nanosecond format
    timezone = pytz.timezone("Europe/Stockholm")  # e.g., "America/New_York"
    start_dt = datetime(date.year, date.month, date.day, tzinfo=timezone)
    end_dt = start_dt + timedelta(days=1)
    start_time_ns = int(start_dt.timestamp()) * 1000000000
    end_time_ns = int(end_dt.timestamp()) * 1000000000

    # Build the Fitness API service
    service = build('fitness', 'v1', credentials=credentials)

    # List all data sources
    data_sources = service.users().dataSources().list(userId='me').execute()

    for source in data_sources.get('dataSource', []):
        data_stream_id = source['dataStreamId']
        print(f"Source: {data_stream_id}")

        # Get dataset for the specific date range for this source
        dataset_id = f"{start_time_ns}-{end_time_ns}"
        dataset = service.users().dataSources().datasets().get(
            userId='me', dataSourceId=data_stream_id, datasetId=dataset_id).execute()

        # Print datapoints for this source
        for point in dataset.get('point', []):
            for value in point.get('value', []):
                print(f"  {point['dataTypeName']}: {value.get('intVal', value.get('fpVal', 'No value'))}")
