import requests
import json


def get_data_from_hh_api(employers_id: list) -> list[dict]:
    data = []
    for employer_id in employers_id:
        response = requests.get(f"https://api.hh.ru/employers/{employer_id}")
        employer_data = json.loads(response.text)

        response2 = requests.get(employer_data['vacancies_url'], params={'per_page': 100})
        vacancies_data = json.loads(response2.text)
        data.append({
            'employer': employer_data,
            'vacancies': vacancies_data['items']
        })

    return data
