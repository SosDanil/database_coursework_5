import requests
import json


def get_employers_from_hh_api(employers_id: list):
    params = {
        "page": 0,
        "per_page": 100
    }
    response = requests.get(f"https://api.hh.ru/vacancies/", params=params)
    hh_data = json.loads(response.text)
    hh_vacancies = hh_data["items"]
    return hh_vacancies
