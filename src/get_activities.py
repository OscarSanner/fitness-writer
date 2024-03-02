import requests
from datetime import datetime, timedelta


def get_strava_activities(strava_creds, date):
    """
    Fetches Strava activities for the authenticated athlete on a specific date and
    aggregates the distance, time, max heart rate, and average heart rate.

    Parameters:
    - strava_creds (dict): A dictionary containing Strava credentials, including the access token.
    - date (datetime.date): The specific date for which to fetch activities.

    Returns:
    - dict: Aggregated information about activities on the specified date.
    """
    access_token = strava_creds.get('access_token')
    if not access_token:
        print("Access token is missing.")
        return None

    # Prepare the date range for filtering activities
    start_date = datetime.combine(date, datetime.min.time())
    end_date = start_date + timedelta(days=1)

    # The Strava API endpoint for listing athlete activities
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}

    # Initialize aggregation variables
    total_distance = 0
    total_time = 0
    max_heart_rate = 0
    avg_heart_rate_accum = 0
    heart_rate_entries = 0

    try:
        # Request activities from Strava
        response = requests.get(url, headers=headers,
                                params={'before': end_date.timestamp(), 'after': start_date.timestamp()})
        response.raise_for_status()
        activities = response.json()

        # Filter and aggregate activities data
        for activity in activities:
            # Aggregate distance (in meters) and moving time (in seconds)
            total_distance += activity.get('distance', 0)
            total_time += activity.get('moving_time', 0)

            # Aggregate heart rate data
            max_hr = activity.get('max_heartrate')
            avg_hr = activity.get('average_heartrate')
            if max_hr:
                max_heart_rate = max(max_heart_rate, max_hr)
            if avg_hr:
                avg_heart_rate_accum += avg_hr
                heart_rate_entries += 1

        # Calculate average heart rate
        avg_heart_rate = avg_heart_rate_accum / heart_rate_entries if heart_rate_entries else 0

        return {
            'distance': total_distance,
            'time': total_time,
            'max_heart_rate': max_heart_rate,
            'avg_heart_rate': avg_heart_rate
        }

    except Exception as e:
        print(f"An error occurred while fetching Strava activities: {e}")
        return None
