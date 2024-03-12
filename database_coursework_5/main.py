import json

from config import config_database
from utils import get_data_from_hh_api, create_database
from config import PATH_TO_JSON_EMPLOYERS_ID


def main():
    with open(PATH_TO_JSON_EMPLOYERS_ID, "r") as file:
        id_data = json.load(file)

    list_employers_id = []
    for value in id_data.values():
        list_employers_id.append(value)

    data = get_data_from_hh_api(list_employers_id)

    params = config_database()
    create_database('course_work_5', params)


main()

# response = requests.get("https://api.hh.ru/employers/5709954")
# hh_data = json.loads(response.text)
# print(hh_data)
# response2 = requests.get(hh_data['vacancies_url'])
# print(response2.text)



