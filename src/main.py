import os

from dotenv import load_dotenv

from authorization import get_google_credentials, get_strava_credentials
from get_steps import get_steps
from datetime import datetime, timedelta

from src.get_activities import get_strava_activities
from src.get_nutrition import get_nutrition
from src.get_resting_ekg import get_resting_heart_rate
from src.get_sleep import get_sleep
from src.get_weight import get_weight
from src.write_to_sheet import insert_data_to_sheet

def main():

    load_dotenv()

    google_creds = get_google_credentials()
    strava_creds = get_strava_credentials()

    chosen_date = (datetime.now() - timedelta(days=1)).date()

    strava_activities = get_strava_activities(strava_creds, chosen_date)
    steps = get_steps(chosen_date, google_creds.token)
    weight = get_weight(chosen_date, google_creds.token)
    nutrition = get_nutrition(chosen_date, google_creds.token)
    sleep = get_sleep(chosen_date, google_creds.token)
    hr = get_resting_heart_rate(chosen_date, google_creds.token)

    print("Steps:", steps)
    print("Weight:", weight)
    print("Sleep:", sleep)
    print("Kcal:", nutrition["kcal"])
    print("Protein:", nutrition["protein"])
    print("Fat:", nutrition["fat"])
    print("Carbohydrates:", nutrition["carbs"])
    print("Resting heart rate:", hr)
    print("R time", strava_activities["time"])
    print("R distance", strava_activities["distance"])
    print("R max hr", strava_activities["max_heart_rate"])
    print("R avg hr", strava_activities["avg_heart_rate"])

    data_values = [
        chosen_date.strftime("%Y-%m-%d"),  # Day remains a string, no rounding needed
        round(nutrition["kcal"] if nutrition["kcal"] is not None else 0, 2),  # Round to 2 decimal places
        round(nutrition["protein"] if nutrition["protein"] is not None else 0, 2),
        round(nutrition["carbs"] if nutrition["carbs"] is not None else 0, 2),
        round(nutrition["fat"] if nutrition["fat"] is not None else 0, 2),
        round(weight if weight is not None else 0, 2),  # Assuming weight could be a floating-point number
        round(sleep if sleep is not None else 0, 2),  # Sleep converted to hours then rounded
        round(hr if hr is not None else 0, 2),  # Assuming heart rate could be a floating-point number
        steps if steps is not None else 0,  # Steps are likely integers, no rounding needed
        round(strava_activities["distance"] / 1000 if strava_activities["distance"] is not None else 0, 2),
        # Distance converted to km then rounded
        round(strava_activities["time"] / 60 if strava_activities["time"] is not None else 0, 2),
        # Time converted to minutes then rounded
        round(strava_activities["avg_heart_rate"] if strava_activities["avg_heart_rate"] is not None else 0, 2),
        # Round avg heart rate
        round(strava_activities["max_heart_rate"] if strava_activities["max_heart_rate"] is not None else 0, 2)
        # Round max heart rate
    ]

    sheet_id = os.getenv("SHEET_ID")

    insert_data_to_sheet(google_creds, sheet_id, chosen_date, data_values)


if __name__ == '__main__':
    main()

