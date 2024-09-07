import os
from abc import ABC, abstractmethod

import psycopg2
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("localhost")
database = os.getenv("postgres")
user = "postgres"
password = os.getenv("password")


class DatabaseCreator(ABC):
    """
    Родительский класс для работы с базами данных
    """

    @abstractmethod
    def create_db(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def insert_table(self):
        pass


class DBCreator(DatabaseCreator):
    """
    Класс создает базу данных по выбранному пользователем названию,
    создает таблицы в этой базе и заполняет их.
    Принимает название базы данных и список вакансий
    Класс DatabaseCreator является родительским классом
    """

    def __init__(self, db_name, data):
        self.db_name = db_name
        self.data = data

    def create_db(self):
        """
        Функция для создания базы данных по названию
        """
        conn_params = {"host": host, "database": database, "user": user, "password": password}
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"DROP DATABASE IF EXISTS {self.db_name} WITH (FORCE)")
        cur.execute(f"CREATE DATABASE {self.db_name}")

        cur.close()
        conn.close()

    def create_table(self):
        """
        Функция для создания таблиц в созданной базе данных
        """
        conn_params = {"host": host, "database": self.db_name, "user": user, "password": password}
        conn = psycopg2.connect(**conn_params)
        try:
            with conn:
                with conn.cursor() as cur:
                    """Создается таблица для работодателей"""
                    cur.execute(
                        """CREATE TABLE IF NOT EXISTS employers
                        (employer_id serial PRIMARY KEY,
                        employer_name varchar(100) NOT NULL UNIQUE);
                        """
                    )
                    """Создается таблица для вакансий работодателей"""
                    cur.execute(
                        """CREATE TABLE IF NOT EXISTS vacancies
                        (vacancy_id serial PRIMARY KEY,
                        vacancy_name varchar(100) NOT NULL,
                        employer_id int NOT NULL,
                        link text NOT NULL,
                        salary INT DEFAULT 0,
                        experience text NOT NULL,
                        description text NOT NULL,
                        area varchar(100) NOT NULL,
                        FOREIGN KEY (employer_id) REFERENCES employers(employer_id));
                        """
                    )
        except Exception as e:
            print(f"Произошла ошибка {e} при создании таблиц")
        else:
            print("Таблицы работодателей и вакансий успешно созданы")
        finally:
            conn.close()

    def insert_table(self):
        """
        Функция для заполнения таблиц
        """
        conn_params = {"host": host, "database": self.db_name, "user": user, "password": password}
        conn = psycopg2.connect(**conn_params)
        try:
            with conn:
                with conn.cursor() as cur:
                    for row in self.data:
                        """Заполняется таблица с работодателями без повторения"""
                        cur.execute(
                            f"INSERT INTO employers (employer_name) VALUES ('{row['employer_name']}') "
                            f"ON CONFLICT (employer_name) DO NOTHING returning employer_id;"
                        )
                        try:
                            emp_id = cur.fetchone()[0]
                        except:
                            pass

                        """Заполняется таблица с вакансиями"""
                        cur.execute(
                            """
                            INSERT INTO vacancies (
                            vacancy_name,
                            employer_id,
                            link,
                            salary,
                            experience,
                            description,
                            area
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                row["vacancy_name"],
                                emp_id,
                                row["link"],
                                row["salary"],
                                row["experience"],
                                row["description"],
                                row["area"],
                            ),
                        )
        except Exception as e:
            print(f"Произошла ошибка {e} при заполнении базы данных")
        else:
            print("База данных успешно заполнена")
        finally:
            conn.close()


if __name__ == "__main__":
    from src.api import HeadHunterAPI

    id_list = [
        "3388",  # Газпромбанк
        "3529",  # СБЕР
        "1440683",  # RUTUBE
        "2624085",  # Вкусно — и точка
        "3776",  # МТС
        "1272486",  # Купер
        "1740",  # Яндекс
        "2180",  # Ozon
        "46587",  # Сима-ленд
        "3127",
    ]  # МегаФон

    hh = HeadHunterAPI()
    hh.load_vacancies(id_list)
    vacancies = hh.get_vacancies()
    db = DBCreator("test", vacancies)
    db.create_db()
    db.create_table()
    db.insert_table()
