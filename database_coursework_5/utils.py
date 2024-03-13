import requests
import json
import psycopg2


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
                company_name VARCHAR(200) NOT NULL,
                company_url VARCHAR(100),
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
                vacancy_name VARCHAR(200) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                vacancy_url  VARCHAR(100),
                published_at DATE
                )
        """)
    conn.commit()
    conn.close()


def save_data_to_database(data: list[dict], database_name, params):
    """Занесение данных о работодателях и вакансиях в таблицу"""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer_data in data:
            employer = employer_data['employer']
            cur.execute(
                """
                INSERT INTO employers (company_name, company_url, city, open_vacancies, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING employer_id
                """,
                (employer['name'], employer['alternate_url'], employer['area']['name'],
                 int(employer['open_vacancies']), employer['description'])
            )
            employer_id = cur.fetchone()[0]
            vacancies_data = employer_data['vacancies']
            for vacancy in vacancies_data:
                if vacancy['salary'] is None:
                    cur.execute(
                        """
                        INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                         published_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (employer_id, vacancy['name'], 0, 0, vacancy['alternate_url'], vacancy['published_at'])
                    )
                elif vacancy['salary']['from'] is None and vacancy['salary']['to'] is not None:
                    cur.execute(
                        """
                        INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                         published_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (employer_id, vacancy['name'], 0, vacancy['salary']['to'],
                         vacancy['alternate_url'], vacancy['published_at'])
                    )
                elif vacancy['salary']['from'] is not None and vacancy['salary']['to'] is None:
                    cur.execute(
                        """
                        INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                         published_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (employer_id, vacancy['name'], vacancy['salary']['from'], 0,
                         vacancy['alternate_url'], vacancy['published_at'])
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                         published_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (employer_id, vacancy['name'], vacancy['salary']['from'], vacancy['salary']['to'],
                         vacancy['alternate_url'], vacancy['published_at'])
                    )

    conn.commit()
    conn.close()
