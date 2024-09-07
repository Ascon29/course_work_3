import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("localhost")
database = os.getenv("postgres")
user = "postgres"
password = os.getenv("password")


class DBManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def __connection(self, query):
        """
        Приватный метод для подключения к таблицам базы данных.
        Принимает sql - запрос от остальных функций в классе
        """
        conn_params = {"host": host, "database": self.db_name, "user": user, "password": password}
        conn = psycopg2.connect(**conn_params)
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
        conn.close()
        return result

    def get_companies_and_vacancies_count(self):
        """
        Функция выдает список всех компаний и количество вакансий у каждой компании
        """
        query = """
                SELECT employer_name, COUNT(*) as vacs_count FROM employers
                JOIN vacancies USING (employer_id)
                GROUP BY employer_name
                """
        return self.__connection(query)

    def get_all_vacancies(self):
        """
        Функция выдает список всех вакансий с указанием названия компании, вакансии, зарплаты и ссылки на вакансию.
        """
        query = """
                    SELECT employer_name, vacancy_name, salary, link FROM vacancies
                    JOIN employers USING (employer_id)
                    ORDER BY employer_name
                    """
        return self.__connection(query)

    def get_avg_salary(self):
        """
        Функция выдает среднюю зарплату по вакансиям.
        НЕ учитывает вакансии, в которых не указана зарплата
        """
        query = """
                    SELECT round(AVG(salary)) as avg_salary FROM vacancies
                    WHERE salary > 0
                    """
        return self.__connection(query)

    def get_vacancies_with_higher_salary(self):
        """
        Функция выдает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        НЕ учитывает вакансии, в которых не указана зарплата
        """
        query = """
                    SELECT * FROM vacancies WHERE salary > (
                    SELECT round(AVG(salary)) as avg_salary FROM vacancies
                    WHERE salary > 0
                    )
                    ORDER BY salary DESC
                    """
        return self.__connection(query)

    def get_vacancies_with_keyword(self, word):
        """
        Функция выдает список всех вакансий, в названии которых содержатся переданные в метод слова, например python.
        """
        query = f"""
                    SELECT * FROM vacancies WHERE vacancy_name LIKE ('%{word}%')
                    """
        return self.__connection(query)


if __name__ == "__main__":
    word = "Python"
    db_manager = DBManager(db_name="test")
    emp_vacs_count = db_manager.get_companies_and_vacancies_count()
    print(emp_vacs_count)

    all_vacs = db_manager.get_all_vacancies()
    print(all_vacs)

    avg_salary = db_manager.get_avg_salary()
    print(avg_salary)

    higher_salary = db_manager.get_vacancies_with_higher_salary()
    print(higher_salary)

    vacs_with_word = db_manager.get_vacancies_with_keyword(word)
    print(vacs_with_word)
