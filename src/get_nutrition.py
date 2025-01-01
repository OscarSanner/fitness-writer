import os
import pathlib
from dotenv import load_dotenv
from lifesum.api import Client
from datetime import date, timedelta
from lifesum.lifesum_requests import GetDiaryRequest, GetDiaryResponse


def get_nutrition(date, lifesum_username, lifesum_password, lifesum_api_endpoint):
    """
    Fetches nutrition information for the specified date using the Google Fitness API.

    Parameters:
    - date (datetime.date): The date for which to fetch nutrition information.
    - google_auth_token (str): Google authorization token.

    Returns:
    - dict: Nutrition information including kcal, protein, carbs, and fat.
    """
    PROJECT_ROOT = pathlib.Path(__file__).parent.resolve().parent.resolve()
    token_file_path = os.path.join(PROJECT_ROOT, "auth_data", "lifesum", "token_file.json")
    client = Client(base_url=lifesum_api_endpoint, password=lifesum_password, username=lifesum_username, token_file_path=token_file_path)

    client.login()
    diary: GetDiaryResponse = client.get_diary(
        GetDiaryRequest(date=date)
    )

    nutrition_totals = {
        'kcal': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0
    }

    nutrition_totals['kcal'] = diary.get_total_nutrient("calories")
    nutrition_totals['protein'] = diary.get_total_nutrient("protein")
    nutrition_totals['carbs'] = diary.get_total_nutrient("carbs")
    nutrition_totals['fat'] = diary.get_total_nutrient("fat")

    return nutrition_totals