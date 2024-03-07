from src.classes import Vacancies, FileManagerJSON


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    while True:
        func = input('''Функционал программы (введите команду):
    Для поиска вакансий в HeadHunter - 1
    Для добавления/удаления собственных вакансии вручную - 2
    Для получения вакансий из файла - 3
    Для завершения программы - stop
    Введите команду: ''')
        if func == 'stop':
            break
        elif func not in ("1", "2", "3"):
            print("Введите правильную цифру или stop")
        elif func == "1":
            query = input('Введите поисковой запрос: ')
            n = input('Введите количество желаемых вакансий: ')
            try:
                n = int(n)
            except:
                n = None
            try:
                vacancy_list = Vacancies.get_vacancies_from_hh(query, n)
                for n, vacancy in enumerate(vacancy_list, start=1):
                    print(f"{n}: {vacancy}")
                if len(vacancy_list) > 0:
                    save_query = input('Желаете сохранить вакансии в файл? y/n: ')
                    if save_query == "y":
                        file_name = input('Введите имя файла: ')
                        file_manager = FileManagerJSON()
                        for v in vacancy_list:
                            file_manager.add_vacancy(v, file_name)
            except ConnectionError:
                print('Ошибка поиска. Попробуйте снова. Либо введите другой запрос')
        elif func == "2":
            file_manager1 = FileManagerJSON()
            add_or_delete_query = input("Добавить вакансию - add, Удалить вакансию - del: ")
            if add_or_delete_query == 'add':
                name = input('Введите название вакансии: ')
                url = input('Введите URL вакансии: ')
                salary_from = int(input('Введите мин. зп: '))
                salary_to = int(input('Введите макс. зп: '))
                currency = input('Введите валюту зп: ')
                respons = input('Введите обязанности: ')
                requirement = input('Введите требования: ')
                v = Vacancies(name, url, salary_from, salary_to, currency, respons, requirement)
                file_name_to_save = input('Введите имя файла: ')
                file_manager1.add_vacancy(v, file_name_to_save)
            elif add_or_delete_query == 'del':
                delete_file = FileManagerJSON()
                name_to_delete = input('Введите название вакансии для удаления: ')
                file_of_vacancy = input('Введите имя файла для удаления вакансии: ')
                delete_file.delete_vacancy_by_name(name_to_delete, file_of_vacancy)
            else:
                print('Введена неверная команда')
        elif func == "3":
            get_vacancies_from_file = FileManagerJSON()
            name_of_file = input('Введите имя файла: ')
            get_vacancies_from_file.get_all_from_file(name_of_file)
