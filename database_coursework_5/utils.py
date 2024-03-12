import requests
import json
import psycopg2


def get_data_from_hh_api(employers_id: list) -> list[dict]:
    data = []
    for employer_id in employers_id:
        response = requests.get(f"https://api.hh.ru/employers/{employer_id}")
        employer_data = json.loads(response.text)

        response2 = requests.get(employer_data['vacancies_url'])
        vacancies_data = json.loads(response2.text)
        data.append({
            'employer': employer_data,
            'vacancies': vacancies_data['items']
        })

    return data


def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о работодателях и их вакансиях."""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employers (
                employer_id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                url VARCHAR(100),
                city VARCHAR(50),
                open_vacancies INTEGER,
                description TEXT
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employers(employer_id),
                name VARCHAR(200) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                url  VARCHAR(100),
                published_at DATE
                )
        """)
    conn.commit()
    conn.close()
