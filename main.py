from src.api import HeadHunterAPI
from src.db_creator import DBCreator
from src.db_manager import DBManager
from user_settings import id_list


def main():
    # подключение к hh через api
    hh = HeadHunterAPI()

    # получение вакансий из списка компаний
    hh.load_vacancies(id_list)
    hh_vacancies = hh.get_vacancies()

    # обращение к пользователю для получения названия для базы данных
    db_name = input("Для создания базы данных, введите ее название: ")
    db = DBCreator(db_name=db_name, data=hh_vacancies)
    db.create_db()
    db.create_table()
    db.insert_table()

    # создается класс для работы с таблицами в созданной базе данных
    db_manager = DBManager(db_name=db_name)

    while True:
        print(
            """
        Эта программа позволяет получить следующую информацию:
        1 - Количество вакансий у каждого работодателя
        2 - Список всех найденных вакансий
        3 - Среднюю зарплату по всем вакансиям (игнорируются вакансии без указания зарплаты)
        4 - Список вакансий, у которых зарплата выше средней среди всех вакансий (игнорируются вакансии без указания зарплаты)
        5 - Список вакансий по ключевому слову
        6 - Завершить работу программы
        """
        )
        user_input = input("Для получения желаемого результата введите число: ")

        # выводит список вакансий отфильтрованный по указанному слову, предлагает попробовать другое слово после вывода
        if user_input == "5":
            while True:
                user_word = input("Введите слово для фильтрации вакансий: ")
                vacs_with_word = db_manager.get_vacancies_with_keyword(user_word)
                for vac in vacs_with_word:
                    print(
                        f"Вакансия: {vac[1]}\nСсылка: {vac[3]}\nЗарплата: {vac[4]}\nОпыт работы: {vac[5]}\nОписание вакансии: {vac[6]}\nГород: {vac[7]}\n"
                    )
                x = input("Попробовать другое слово? (да / нет) ").lower()
                if x == "нет":
                    break

        # выводит список вакансий, у которых зарплата выше средней
        elif user_input == "4":
            higher_salary = db_manager.get_vacancies_with_higher_salary()
            for vac in higher_salary:
                print(
                    f"Вакансия: {vac[1]}\nСсылка: {vac[3]}\nЗарплата: {vac[4]}\nОпыт работы: {vac[5]}\nОписание вакансии: {vac[6]}\nГород: {vac[7]}\n"
                )

        # среднюю зарплату по всем вакансиям
        elif user_input == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"Средняя зарплата по всем вакансиям: {avg_salary[0][0]}")

        # выводит список всех найденных вакансий
        elif user_input == "2":
            all_vacs = db_manager.get_all_vacancies()
            for vac in all_vacs:
                print(f"Компания: {vac[0]}\nВакансия: {vac[1]}\nЗарплата: {vac[2]}\nСсылка: {vac[3]}\n")

        # выводит количество вакансий у каждого работодателя
        elif user_input == "1":
            emp_vacs_count = db_manager.get_companies_and_vacancies_count()
            for vac in emp_vacs_count:
                print(f"Компания: {vac[0]}\nКоличество вакансий: {vac[1]}\n")

        # завершает работу программы
        elif user_input == "6":
            print("Программа завершает свою работу")
            break


if __name__ == "__main__":
    main()
