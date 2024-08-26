import json
from abc import ABC, abstractmethod

import requests


class Parser(ABC):
    """
    Абстрактный родительский класс для подключения по API
    """

    @abstractmethod
    def load_vacancies(self, keyword, employer_list):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunterAPI(Parser):
    """
    Класс для работы с API HeadHunter
    Класс Parser является родительским классом
    """

    def __init__(self):
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.vacancies = []
        self.validate_vacancies = []

    def load_vacancies(self, employer_list, keyword=""):
        """
        Функция для получения вакансий по заданному слову.
        Приводит полученный список к нужному виду.
        """
        self.params["text"] = keyword
        while self.params.get("page") != 2:
            try:
                response = requests.get(self.__url, headers=self.__headers, params=self.params)
            except Exception as e:
                print(f"Произошла ошибка {e}")
            else:
                vacancies = response.json()["items"]
                self.vacancies.extend(vacancies)
                self.params["page"] += 1

        for vacancy in self.vacancies:
            if vacancy["employer"]["name"] in employer_list:
                employer_id = vacancy["employer"]["id"]
                employer_name = vacancy["employer"]["name"]
                vacancy_name = vacancy["name"] if vacancy["name"] else "Название не указано"
                link = vacancy["alternate_url"] if vacancy["alternate_url"] else "Ссылка отсутствует"
                if vacancy["salary"] is None or vacancy["salary"]["from"] is None or vacancy["salary"]["to"] is None:
                    salary = 0
                elif vacancy["salary"]["from"]:
                    salary = vacancy["salary"]["from"]
                elif vacancy["salary"]["to"]:
                    salary = vacancy["salary"]["to"]
                experience = vacancy["experience"]["name"] if vacancy["experience"] else "Опыт работы не указан"
                description = vacancy["snippet"]["responsibility"] if vacancy["snippet"] else "Описание отсутствует"
                area = vacancy["area"]["name"] if vacancy["area"] else "Город не указан"
                self.validate_vacancies.append(
                    {
                        "vacancy_name": vacancy_name,
                        "employer_id": employer_id,
                        "employer_name": employer_name,
                        "link": link,
                        "description": description,
                        "experience": experience,
                        "salary": salary,
                        "area": area,
                    }
                )

    def get_vacancies(self):
        """
        Возвращает список вакансий
        """
        return self.validate_vacancies


if __name__ == "__main__":
    emp_list = [
        "Газпромбанк",
        "СБЕР",
        "RUTUBE",
        "Вкусно — и точка",
        "МТС",
        "Купер",
        "Яндекс",
        "Ozon",
        "Сима-ленд",
        "МегаФон",
    ]
    hh = HeadHunterAPI()
    hh.load_vacancies(emp_list, "Python")
    hh_vacancies = hh.get_vacancies()
    print(hh_vacancies)

    with open("vacs.json", "w", encoding="utf-8") as f:
        json.dump(hh_vacancies, f, ensure_ascii=False, indent=4)
