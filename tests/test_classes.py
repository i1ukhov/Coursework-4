from src.classes import HeadHunterAPI, Vacancies
import pytest


def test_hh_api():
    hh = HeadHunterAPI()
    assert len(hh.get_vacancies('Python')) > 0


@pytest.fixture
def user_vacancy():
    v1 = Vacancies('Python-developer', 'url', 50000, 60000, 'RUB', '', '')
    return v1


def test_vacancies(user_vacancy):
    assert isinstance(user_vacancy, Vacancies)
