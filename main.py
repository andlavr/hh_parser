import os

import time
import traceback
import requests

import typing

from bs4 import BeautifulSoup

from conf import headers


def get_bs_page(url: str, headers: dict) -> BeautifulSoup:
    """
    Получение страницы по url

    :param url: url страницы
    :param headers: передаваемые вместе с url заголовки (headers)
    :return: страница в виде объекта BeautifulSoup
    """

    response = requests.get(url.strip(), headers=headers, timeout=10)
    bs = BeautifulSoup(response.text, features='html.parser')

    return bs


def is_valid_url_vacancy(url:str) -> bool:
    """
    Проверка url на то, что он ссылается на вакансию

    :param url: url страницы
    :return: True|False
    """
    if '/vacancy/' in url:
        return True
    return False


def is_valid_url_vacancy_for_update(url: str, current_urls: list) -> bool:
    """
    Проверка вакансии на актуальность (валидность для добавления)

    :param url: url страницы
    :param current_urls: список добавленных вакансий
    :return: True|False
    """
    if '/vacancy/' not in url or not url.startswith('https') or url in current_urls:
        return False
    return True


def update_file(file_name: str|os.PathLike, url: str) -> None:
    """
    Дозапись вакансии в файл

    :param file_name:  путь к .txt файлу, где будут храниться ссылки
    :param url: добавляемый url адрес
    :return: None
    """

    if not file_name.endswith('.txt'):
        raise NameError("Файл не является .txt форматом")

    try:
        with open(file_name, "a") as f:
            f.write(f'\n{url}')
    except:
        traceback.print_exc()
        print(url)


def get_current_urls(output_file) -> list[str]:
    """
    Получение ссылок из файла

    :param output_file: путь к .txt файлу, где хранятся ссылки
    :return: список ссылок
    """
    with open(output_file, 'r') as my_file:
        data = my_file.read()



    if not data:
        return []
    return data.split('\n')


def check_output_file(output_file) ->None:
    """
    Проверка наличия файла, если нет то создание его

    :param output_file: путь к .txt файлу где должны храниться ссылки
    :return: None
    """
    if not os.path.exists(output_file):
        with open(output_file, 'w') as f:
            pass


def update_vacancies(url: str, headers: str, output_file="vacancies.txt") ->None:
    """
    Основная функция для обновления ссылок в файле

    :param url: url страницы
    :param headers: передаваемые вместе с url загаловки (headers)
    :param output_file: путь к .txt файлу

    :return: None
    """
    check_output_file(output_file)

    current_urls = get_current_urls(output_file)

    page = get_bs_page(url, headers)

    update_file(output_file, time.ctime())

    for elem in page.main.find_all('a'):
        link = elem['href']

        if not is_valid_url_vacancy(link):
            continue

        time.sleep(2)

        sub_page = get_bs_page(link, headers)

        for elem in sub_page.find_all('a'):
            vacancy_url = elem['href']

            print("Checking:", vacancy_url)

            if not is_valid_url_vacancy_for_update(vacancy_url, current_urls):
                continue

            update_file(output_file, f"{time.ctime()} >>> {vacancy_url}")

            current_urls.append(vacancy_url)
            print("Adding", vacancy_url)


if __name__ == '__main__':
    # url = "https://spb.hh.ru/search/vacancy?text=Python+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA+%D0%B1%D0%B5%D0%B7+%D0%BE%D0%BF%D1%8B%D1%82%D0%B0+%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%8B&from=suggest_post&area=2&hhtmFrom=vacancy&hhtmFromLabel=vacancy_search_line"
    url = "https://spb.hh.ru/search/vacancy?from=suggest_post&area=2&hhtmFrom=main&hhtmFromLabel=vacancy_search_line&experience=noExperience&search_field=name&search_field=company_name&search_field=description&text=Python+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA&enable_snippets=false"
    update_vacancies(url, headers, 'vacancies.txt')
