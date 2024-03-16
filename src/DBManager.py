import psycopg2


class DBManager:
    def __init__(self, database_name: str, params: dict):
        self.database_name = database_name
        self.parameters = params

    def create_database(self):
        """Создает базу данных"""

        conn = psycopg2.connect(dbname='postgres', **self.parameters)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"DROP DATABASE {self.database_name}")
        cur.execute(f"CREATE DATABASE {self.database_name}")

        conn.close()

    def create_tables(self):
        """Создает таблицы в базе данных для сохранения информации о работодателях и их вакансиях"""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
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

    def save_data_to_database(self, data: list[dict]):
        """Занесение данных о работодателях и вакансиях в таблицу"""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
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
                            (employer_id, vacancy['name'].lower(), 0, 0, vacancy['alternate_url'],
                             vacancy['published_at'])
                        )
                    elif vacancy['salary']['from'] is None and vacancy['salary']['to'] is not None:
                        cur.execute(
                            """
                            INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                             published_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (employer_id, vacancy['name'].lower(), 0, vacancy['salary']['to'],
                             vacancy['alternate_url'], vacancy['published_at'])
                        )
                    elif vacancy['salary']['from'] is not None and vacancy['salary']['to'] is None:
                        cur.execute(
                            """
                            INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                             published_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (employer_id, vacancy['name'].lower(), vacancy['salary']['from'], 0,
                             vacancy['alternate_url'], vacancy['published_at'])
                        )
                    else:
                        cur.execute(
                            """
                            INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, vacancy_url,
                             published_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (employer_id, vacancy['name'].lower(), vacancy['salary']['from'], vacancy['salary']['to'],
                             vacancy['alternate_url'], vacancy['published_at'])
                        )

        conn.commit()
        conn.close()

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании"""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT company_name, COUNT(*) FROM employers
            JOIN vacancies USING(employer_id)
            GROUP BY company_name
            """
            )
            companies = cur.fetchall()
        conn.commit()
        conn.close()
        for company in companies:
            print(f"Название компании: {company[0]}\n"
                  f"Количество вакансий: {company[1]}\n")

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
         названия вакансии, зарплаты и ссылки на вакансию"""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
                FROM vacancies JOIN employers USING (employer_id)
                """
            )
            vacancies = cur.fetchall()
        conn.commit()
        conn.close()
        for vacancy in vacancies:
            if vacancy[2] == 0 and vacancy[3] == 0:
                print(f"Название компании: {vacancy[0]}\n"
                      f"Название должности: {vacancy[1]}\n"
                      f"Зарплата не указана\n"
                      f"Ссылка на вакансию: {vacancy[4]}\n")
            elif vacancy[2] == 0:
                print(f"Название компании: {vacancy[0]}\n"
                      f"Название должности: {vacancy[1]}\n"
                      f"Зарплата до {vacancy[3]}\n"
                      f"Ссылка на вакансию: {vacancy[4]}\n")
            elif vacancy[3] == 0:
                print(f"Название компании: {vacancy[0]}\n"
                      f"Название должности: {vacancy[1]}\n"
                      f"Зарплата от {vacancy[2]}\n"
                      f"Ссылка на вакансию: {vacancy[4]}\n")
            else:
                print(f"Название компании: {vacancy[0]}\n"
                      f"Название должности: {vacancy[1]}\n"
                      f"Зарплата от {vacancy[2]} до {vacancy[3]}\n"
                      f"Ссылка на вакансию: {vacancy[4]}\n")

    def get_avr_salary(self):
        """Получает среднюю зарплату по вакансиям."""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG(salary_from), AVG(salary_to) FROM vacancies
                """
            )
            average_salary = cur.fetchall()
        conn.commit()
        conn.close()

        print(f"Средняя зарплата от: {average_salary[0][0]} руб.\n"
              f"Средняя зарплата до: {average_salary[0][1]} руб.\n")

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        Смотрим только по зарплатам "от" - они в приоритете"""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT vacancy_name, salary_from, salary_to, vacancy_url FROM vacancies
                WHERE salary_from > (SELECT AVG(salary_from) FROM vacancies)
                """
            )
            vacancies = cur.fetchall()
        conn.commit()
        conn.close()

        for vacancy in vacancies:
            if vacancy[2] == 0:
                print(f"Название должности: {vacancy[0]}\n"
                      f"Зарплата от: {vacancy[1]} руб.\n"
                      f"Ссылка на вакансию: {vacancy[3]}\n")
            else:
                print(f"Название должности: {vacancy[0]}\n"
                      f"Зарплата от: {vacancy[1]} руб.\n"
                      f"Зарплата до: {vacancy[2]} руб.\n"
                      f"Ссылка на вакансию: {vacancy[3]}\n")

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python."""

        conn = psycopg2.connect(dbname=self.database_name, **self.parameters)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT vacancy_name, salary_from, salary_to, vacancy_url FROM vacancies
                WHERE vacancy_name LIKE '{keyword}%' OR vacancy_name LIKE '%{keyword}'
                OR vacancy_name LIKE '%{keyword}%'
                """
            )
            vacancies = cur.fetchall()
        conn.commit()
        conn.close()

        for vacancy in vacancies:
            if vacancy[1] == 0 and vacancy[2] == 0:
                print(f"Название должности: {vacancy[0]}\n"
                      f"Зарплата не указана\n"
                      f"Ссылка на вакансию: {vacancy[3]}\n")
            elif vacancy[1] == 0:
                print(f"Название должности: {vacancy[0]}\n"
                      f"Зарплата до {vacancy[2]}\n"
                      f"Ссылка на вакансию: {vacancy[3]}\n")
            elif vacancy[2] == 0:
                print(f"Название должности: {vacancy[0]}\n"
                      f"Зарплата от {vacancy[1]}\n"
                      f"Ссылка на вакансию: {vacancy[3]}\n")
            else:
                print(f"Название должности: {vacancy[0]}\n"
                      f"Зарплата от {vacancy[1]} до {vacancy[2]}\n"
                      f"Ссылка на вакансию: {vacancy[3]}\n")
