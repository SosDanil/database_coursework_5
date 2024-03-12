import json
import requests

from utils import get_data_from_hh_api
from config import PATH_TO_JSON_EMPLOYERS_ID


with open(PATH_TO_JSON_EMPLOYERS_ID, "r") as file:
    data = json.load(file)

list_employers_id = []
for value in data.values():
    list_employers_id.append(value)

data = get_data_from_hh_api(list_employers_id[0:2])
print(data)


# response = requests.get("https://api.hh.ru/employers/5709954")
# hh_data = json.loads(response.text)
# print(hh_data)
# response2 = requests.get(hh_data['vacancies_url'])
# print(response2.text)



