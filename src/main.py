import json

from config import config_database
from utils import get_data_from_hh_api
from config import PATH_TO_JSON_EMPLOYERS_ID
from DBManager import DBManager


def main():
    with open(PATH_TO_JSON_EMPLOYERS_ID, "r") as file:
        id_data = json.load(file)

    list_employers_id = []
    for value in id_data.values():
        list_employers_id.append(value)

    hh_data = get_data_from_hh_api(list_employers_id)

    params = config_database()
    db_manager = DBManager('course_work_5', params)

    db_manager.create_database()
    db_manager.create_tables()
    db_manager.save_data_to_database(hh_data)
    db_manager.get_companies_and_vacancies_count()
    db_manager.get_all_vacancies()
    db_manager.get_avr_salary()
    db_manager.get_vacancies_with_higher_salary()

    keyword = input("Введите название вакансии").lower()
    db_manager.get_vacancies_with_keyword(keyword)


main()
