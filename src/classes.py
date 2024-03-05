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
    def save_vacancies(self, query):
        pass


class HeadHunterAPI(APIBase):
    """Класс API HeadHunter"""

    def __repr__(self):
        return f'Класс {self.__class__.__name__} подключается к API HH и получает вакансии'

    def get_vacancies(self, query):
        """Получение списка вакансий по запросу через API"""
        vacancies_list = []
        if isinstance(query, str):
            parameters = {'text': f'NAME:{query}', 'per_page': 100, }
            response = requests.get(f'https://api.hh.ru/vacancies', parameters)
            if response.status_code == 200:
                num_of_pages = int(json.loads(response.text)['pages'])
                if num_of_pages == 0:
                    return 'Нет вакансий по запросу'
                elif num_of_pages == 1:
                    new_parameters = {'text': f'NAME:{query}', 'per_page': 100, }
                    new_response = requests.get(f'https://api.hh.ru/vacancies', new_parameters)
                    vacancies_list = (json.loads(new_response.text)['items'])
                    return vacancies_list
                else:
                    for i in range(num_of_pages+1):
                        new_parameters = {'text': f'NAME:{query}', 'per_page': 100, 'pages': i, }
                        new_response = requests.get(f'https://api.hh.ru/vacancies', new_parameters)
                        vacancies_list.extend(json.loads(new_response.text)['items'])
                    return vacancies_list
            else:
                print('Возникла ошибка при подключении к API')
        else:
            print(f'{query} - некорректный запрос. Введите корректное название вакансии')

    def save_vacancies(self, query):
        """Сохранить вакансии в json-файл"""
        get_vacancies_data = self.get_vacancies(query)
        if get_vacancies_data is not None and get_vacancies_data != []:
            file_path = os.path.join("..", "data", "vacancies.json")
            with open(file_path, 'w+', encoding='utf-8') as f:
                vacancies_json = json.dumps(get_vacancies_data, ensure_ascii=False)
                f.write(vacancies_json)
                print('Вакансии записаны в файл в папку data')
        else:
            print('Нет данных для сохранения. Файл не был создан')
