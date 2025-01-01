from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

class GoogleFitness:
    def __init__(self, google_auth_token):
        self.credentials = Credentials(token=google_auth_token)
        self.service = build('fitness', 'v1', credentials=self.credentials)

    def _get_data(self, data_source, start_dt, end_dt):
        """ Helper method to fetch dataset from Google Fitness API """
        timezone = pytz.timezone("Europe/Stockholm")
        start_time_ns = int(start_dt.timestamp()) * 10**9
        end_time_ns = int(end_dt.timestamp()) * 10**9
        dataset_id = f"{start_time_ns}-{end_time_ns}"
        data = self.service.users().dataSources().datasets().get(
            userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()
        return data

    def get_resting_heart_rate(self, date):
        """ Fetches the resting heart rate for the specified date """
        start_dt = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Stockholm"))
        end_dt = start_dt + timedelta(days=1)
        data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate"
        data = self._get_data(data_source, start_dt, end_dt)
        heart_rates = [point['value'][0]['fpVal'] for point in data.get('point', []) if 'fpVal' in point['value'][0]]
        return min(heart_rates) if heart_rates else None

    def get_sleep(self, date):
        """ Fetches sleep data for the specified date and aggregates total sleep time """
        start_dt = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Stockholm"))
        end_dt = start_dt + timedelta(days=1)
        data_source = "derived:com.google.sleep.segment:com.google.android.gms:merge_sleep_segments"
        data = self._get_data(data_source, start_dt, end_dt)
        total_sleep_time_seconds = 0
        for point in data.get('point', []):
            sleep_duration_seconds = (int(point['endTimeNanos']) - int(point['startTimeNanos'])) / 1e9
            total_sleep_time_seconds += sleep_duration_seconds
        return total_sleep_time_seconds / 3600

    def get_steps(self, date):
        """ Fetches the steps taken on the specified date """
        start_dt = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Stockholm"))
        end_dt = start_dt + timedelta(days=1)
        data_source = "raw:com.google.step_count.delta:com.sec.android.app.shealth:health_platform"
        data = self._get_data(data_source, start_dt, end_dt)
        steps = 0
        for point in data.get('point', []):
            if 'intVal' in next(filter(lambda x: 'intVal' in x, point['value']), None):
                steps += sum(value['intVal'] for value in point['value'] if 'intVal' in value)
        return steps

    def get_weight(self, date):
        """ Fetches the latest weight measurement registered before the specified date """
        start_dt = datetime(date.year - 5, 1, 1, tzinfo=pytz.timezone("Europe/Stockholm"))
        end_dt = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Stockholm"))
        data_source = "derived:com.google.weight:com.google.android.gms:merge_weight"
        data = self._get_data(data_source, start_dt, end_dt)
        weight_measurements = [point for point in data.get('point', []) if int(point['endTimeNanos']) < int(end_dt.timestamp()) * 1e9]
        return max([point['value'][0]['fpVal'] for point in weight_measurements], default=None) if weight_measurements else None