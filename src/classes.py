from abc import ABC, abstractmethod
import requests
import json
import os


class APIBase(ABC):

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_vacancies(self, query):
        pass

    @abstractmethod
    def save_vacancies(self, query, filename):
        pass


class HeadHunterAPI(APIBase):
    """Класс API HeadHunter"""

    def __repr__(self):
        return f'Класс {self.__class__.__name__} подключается к API HH и получает вакансии'

    def get_vacancies(self, query):
        """Получение списка вакансий по запросу через API"""
        vacancies_list = []
        if isinstance(query, str):
            parameters = {'text': f'NAME:{query}', 'per_page': 100, 'only_with_salary': True,
                          'order_by': 'salary_desc', }
            response = requests.get(f'https://api.hh.ru/vacancies', parameters)
            if response.status_code == 200:
                num_of_pages = int(json.loads(response.text)['pages'])
                if num_of_pages == 0:
                    return 'Нет вакансий по запросу'
                elif num_of_pages == 1:
                    new_parameters = {'text': f'NAME:{query}', 'per_page': 100, 'only_with_salary': True,
                                      'order_by': 'salary_desc', }
                    new_response = requests.get(f'https://api.hh.ru/vacancies', new_parameters)
                    vacancies_list = (json.loads(new_response.text)['items'])
                    return vacancies_list
                else:
                    for i in range(num_of_pages + 1):
                        new_parameters = {'text': f'NAME:{query}', 'per_page': 100, 'pages': i,
                                          'only_with_salary': True, 'order_by': 'salary_desc', }
                        new_response = requests.get(f'https://api.hh.ru/vacancies', new_parameters)
                        vacancies_list.extend(json.loads(new_response.text)['items'])
                    return vacancies_list
            else:
                print('Возникла ошибка при подключении к API')
        else:
            print(f'{query} - некорректный запрос. Введите корректное название вакансии')

    def save_vacancies(self, query, filename):
        """Сохранить вакансии в json-файл"""
        get_vacancies_data = self.get_vacancies(query)
        if get_vacancies_data is not None and get_vacancies_data != [] and isinstance(get_vacancies_data, list):
            file_path = os.path.join("data", f"{filename}")
            with open(file_path, 'w+', encoding='utf-8') as file:
                vacancies_json = json.dumps(get_vacancies_data, ensure_ascii=False)
                file.write(vacancies_json)
                print('Вакансии записаны в файл в папку data')
        else:
            print('Нет данных для сохранения. Файл не был создан')


class Vacancies:
    """Класс для работы с вакансиями"""
    name: str
    url: str
    salary_from: int or float or str
    salary_to: int or float or str
    currency: str
    responsibility: str
    requirements: str

    def __init__(self, name, url, salary_from, salary_to, currency, responsibility, requirements):
        self.name = name
        self.url = url
        self.currency = currency
        if salary_from is None:
            self.salary_from = 'Минимальная зарплата не указана'
        else:
            self.salary_from = salary_from
        if salary_to is None:
            self.salary_to = 'Максимальная зарплата не указана'
        else:
            self.salary_to = salary_to
        if responsibility is None:
            self.responsibility = 'Нет описания'
        else:
            self.responsibility = responsibility
        self.requirements = requirements

    def __str__(self):
        return f'{self.name}, {self.url}, ({self.salary_from}-{self.salary_to}) {self.currency}'

    def __repr__(self):
        return f'Объект класса: {self.__class__.__name__}'

    @property
    def check_validation(self):
        """Валидация по зарплате"""
        if isinstance(self.salary_from, (int, float)):
            if self.salary_from > 0:
                return True
            return False
        else:
            return False

    @staticmethod
    def get_vacancies_from_hh(query, n=None):
        """Получение вакансий из HH. Преобразование. Вывод N числа вакансий по запросу query"""
        vacancies = HeadHunterAPI().get_vacancies(query)
        formatted_vacancies_list = []
        if n is not None and isinstance(n, int) and n > 0:
            search_vacancies = vacancies[:n]
        else:
            search_vacancies = vacancies
        for vacancy in search_vacancies:
            name = vacancy.get('name')
            url = vacancy.get('alternate_url')
            salary = vacancy.get('salary')
            salary_from = salary.get('from')
            salary_to = salary.get('to')
            currency = salary.get('currency')
            responsibility = vacancy.get('snippet')['responsibility']
            requirements = vacancy.get('snippet')['requirement']
            f_vacancy = Vacancies(name, url, salary_from, salary_to, currency, responsibility, requirements)
            formatted_vacancies_list.append(f_vacancy)
        if len(formatted_vacancies_list) == 0:
            print(f'Ничего не найдено по запросу "{query}"')
        return formatted_vacancies_list

    @staticmethod
    def compare_vacancies_by_salary(first_vacancy, second_vacancy):
        if isinstance(first_vacancy, Vacancies) and isinstance(second_vacancy, Vacancies):
            if first_vacancy.check_validation and second_vacancy.check_validation:
                result = [second_vacancy, first_vacancy][first_vacancy.salary_from > second_vacancy.salary_from]
                return result.name, result.salary_from, result.currency
            else:
                return "Проверьте, что зарплата указана"
        else:
            return 'Переданы не объекты класса Vacancies'

    @property
    def formatted_vacancy(self):
        return {'name': self.name, 'url': self.url, 'salary': {'to': self.salary_to,
                                                               'from': self.salary_from,
                                                               'currency': self.currency},
                'snippet': {'responsibility': self.responsibility, 'requirement': self.requirements}}


class FileManager(ABC):
    """Абстрактный класс для работы с файлами"""

    @staticmethod
    @abstractmethod
    def add_vacancy(vacancy, filename):
        pass

    @staticmethod
    @abstractmethod
    def delete_vacancy_by_name(name, filename):
        pass

    @abstractmethod
    def save_to_file_list_of_vacancies(self, vacancies, filename):
        pass

    @abstractmethod
    def get_from_file_filtered_by_salary(self, salary, filename):
        pass

    @staticmethod
    @abstractmethod
    def get_all_from_file(filename):
        pass


class FileManagerJSON(FileManager):
    """Класс для работы с файлами JSON"""

    def __repr__(self):
        return f'Объект класса {self.__class__.__name__}'

    @staticmethod
    def add_vacancy(vacancy, filename):
        """Функция добавления вакансии в файл. Если файла нет, создается новый"""
        if isinstance(vacancy, Vacancies):
            file_path = os.path.join("data", f"{filename}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read()
                    vacancies_list = json.loads(data)
                    new_vacancy = [vacancy.formatted_vacancy]
                    vacancies_list.extend(new_vacancy)
                with open(file_path, 'w', encoding='utf-8') as fi:
                    vacancies_json = json.dumps(vacancies_list, ensure_ascii=False)
                    fi.write(vacancies_json)
                    print(f'Вакансия записана в файл {filename} в папке data')
            except FileNotFoundError:
                print(f'Файла {filename} не существует. Будет создан новый файл.')
                with open(file_path, 'a+', encoding='utf-8') as file:
                    vacancies_json = json.dumps([vacancy.formatted_vacancy], ensure_ascii=False)
                    file.write(vacancies_json)
        else:
            print('Передайте объект класса Vacancies. Запись не выполнена')

    @staticmethod
    def delete_vacancy_by_name(name, filename):
        file_path = os.path.join("data", f"{filename}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                vacancies_list = json.loads(data)
                new_vacancies_list = []
                for vacancy in vacancies_list:
                    if vacancy.get('name') != name:
                        new_vacancies_list.append(vacancy)
                if len(vacancies_list) == len(new_vacancies_list):
                    print('Вакансия не была удалена. Проверьте имя вакансии')
                else:
                    print(f'Удалено {len(vacancies_list) - len(new_vacancies_list)} вакансии по запросу ({name})')
            with open(file_path, 'w', encoding='utf-8') as fi:
                vacancies_json = json.dumps(new_vacancies_list, ensure_ascii=False)
                fi.write(vacancies_json)
        except FileNotFoundError:
            print(f"Файл с именем {filename} не найден")

    def save_to_file_list_of_vacancies(self, vacancies, filename):
        pass

    def get_from_file_filtered_by_salary(self, salary, filename):
        pass

    @staticmethod
    def get_all_from_file(filename):
        file_path = os.path.join("data", f"{filename}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                vacancies_list = json.loads(data)
                for n, vacancy in enumerate(vacancies_list, start=1):
                    name = vacancy.get('name')
                    url = vacancy.get('url')
                    salary = vacancy.get('salary')
                    salary_from = salary.get('from')
                    salary_to = salary.get('to')
                    currency = salary.get('currency')
                    responsibility = vacancy.get('snippet')['responsibility']
                    requirements = vacancy.get('snippet')['requirement']
                    print(
                        f"{n}: {Vacancies(name, url, salary_from, salary_to, currency, responsibility, requirements)}")
        except FileNotFoundError:
            print(f'Файл с именем {filename} не найден в папке data')


# class FileManagerCSV(FileManager):
#     """Класс для работы с файлами CSV"""

# class FileManagerExcel(FileManager):
#     """Класс для работы с файлами Excel"""

# class FileManagerTXT(FileManager):
#     """Класс для работы с файлами txt"""

# hh = HeadHunterAPI()
# for v in hh.get_vacancies('Python')[0:4]:
#     print(v)
# hh.save_vacancies('Python', 'test.json')
# v1 = Vacancies('Python-developer', 'url', 50000, 60000, 'RUB', '', '')
# v2 = Vacancies('Java-developer', 'url', 40000, 50000, 'RUB', '', '')
# v3 = Vacancies('Java-developer', 'url', '', 100000, 'RUB', '', '')
#
# print(Vacancies.compare_vacancies_by_salary(v1, v2))
# print(Vacancies.compare_vacancies_by_salary(v1, v3))

# for n, i in enumerate(Vacancies.get_vacancies_from_hh('Python', 10), start=1):
#     print(f'{n}: {i}')

# #
# f = FileManagerJSON()
# f.add_vacancy(v1, 'vacancies.json')
# f.add_vacancy(v2, 'vacancies.json')

# f.get_all_from_file('vacsfies.json')
# f.get_all_from_file('vacancies.json')
# f.get_all_from_file('test.json')
# f.delete_vacancy_by_name('Python-developer', 'vacancies.json')
# f.get_all_from_file('vacancies.json')
