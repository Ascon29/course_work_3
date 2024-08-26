import os
from abc import ABC, abstractmethod

import psycopg2
from dotenv import load_dotenv

load_dotenv()
password = os.getenv("DATABASE_PASSWORD")


class DatabaseCreator(ABC):

    @abstractmethod
    def create_db(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def fill_table(self):
        pass


class DBCreator(DatabaseCreator):

    def __init__(self, db_name, data):
        self.db_name = db_name
        self.data = data

    def create_db(self):
        conn_params = {"host": "localhost", "database": "postgres", "user": "postgres", "password": password}
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute(f"CREATE DATABASE {self.db_name}")
        except:
            pass
        cur.close()
        conn.close()

    def create_table(self):
        conn_params = {"host": "localhost", "database": self.db_name, "user": "postgres", "password": password}
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS employers
            (employer_id serial PRIMARY KEY,
            employer_name text NOT NULL);
            """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS vacancies
            (vacancy_id serial PRIMARY KEY,
            vacancy_name text NOT NULL,
            employer_id int NOT NULL,
            employer_name text NOT NULL,
            link text NOT NULL,
            salary INT NOT NULL,
            experience text NOT NULL,
            description text NOT NULL,
            area text NOT NULL,
            FOREIGN KEY (employer_id) REFERENCES employers(employer_id));
            """
        )

        conn.commit()
        cur.close()
        conn.close()

    def fill_table(self):
        conn_params = {"host": "localhost", "database": self.db_name, "user": "postgres", "password": password}
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        pass


if __name__ == "__main__":
    from src.api import HeadHunterAPI

    hh = HeadHunterAPI()
    vacancies = hh.get_vacancies()
    db = DBCreator("test", vacancies)
    db.create_db()
    db.create_table()
