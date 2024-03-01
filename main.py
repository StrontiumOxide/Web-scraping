import re
import json
import requests
import bs4
import fake_headers
import time


def generate_headers() -> dict:

    """
    Данная функция необходима для создания фейковых заголовков,\n
    чтобы сайты нас не забанили.
    """

    return fake_headers.Headers(browser="chrome", os="win").generate()


def dump_json(information: list[dict]) -> None:

    """
    Функция для записи информации в JSON-файл.
    """

    with open(file="Вакансии.json", mode="w", encoding="utf-8-sig") as file:
        json.dump(information, file, ensure_ascii=False, indent=2)


def chronometer(func):

    """
    Декоратор для фиксирования времени выполнения функций.
    """

    def wrapper(*args, **kwargs):

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} создала JSON-файл за {execution_time:.2f} секунд")
        return result
    
    return wrapper

@chronometer
def main() -> None:

    """
    Главная функция.
    """

    main_URL = r"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"

        # Обход всех страниц на сайте.
    number_list = 0
    all_list = []
    while True:

            # Отправление запроса на сайт на определённую страницу. Получение HTML-кода страницы
        response = requests.get(url=f"{main_URL}&page={number_list}", headers=generate_headers())

        if response.status_code == 200:

            print(f'ОБРАБОТКА СТРАНИЦЫ ПОД НОМЕРОМ: "{number_list+1}"')

            main_html_text = response.text
            main_page = bs4.BeautifulSoup(markup=main_html_text, features="lxml")
            vacancy_page = main_page.find(name="div", attrs={"data-qa": "vacancy-serp__results", "id": "a11y-main-content"})
            list_vacancy = vacancy_page.find_all(name="span", attrs={"class": "serp-item__title-link-wrapper"})

                # Обход всех вакансий на одной странице
            for vacancy in list_vacancy:

                    # Получение ссылки на определённую вакансию
                vacancy_link = vacancy.find(name="a", attrs={"class": "bloko-link"}).get("href")

                    # Отправление запроса по вакансии. Получение HTML-кода страницы
                response_2 = requests.get(url=vacancy_link, headers=generate_headers())
                local_html_text = response_2.text
                local_page = bs4.BeautifulSoup(markup=local_html_text, features="lxml")

                    # Получение описание вакансии
                obj_description_vacancy = local_page.find(name="div", attrs={"class": "vacancy-description"})

                try:
                    description_vacancy = obj_description_vacancy.text
                except AttributeError:
                    continue

                    # Проверка на вхождения слов Django и Flask в описание вакансии
                if re.search(pattern=r"[D,d]jango|[F,f]lask", string=description_vacancy):

                        # Получение "объектов" 
                    obj_title = local_page.find(name="div", attrs={"class": "vacancy-title"}).\
                                       find(name="h1", attrs={"data-qa": "vacancy-title", "class": "bloko-header-section-1"})
                    
                    obj_salary = local_page.find(name="div", attrs={"class": "vacancy-title"}).\
                                       find(name="div", attrs={"data-qa": "vacancy-salary"})
                    
                    obj_company_name = local_page.find(name="span", attrs={"class": "vacancy-company-name"})

                    obj_sity = local_page.find(name="p", attrs={"data-qa": "vacancy-view-location"})

                        # Проверки на NoneType и запись в словари
                    active_list = [obj_title, obj_salary, obj_company_name, obj_sity]
                    name_list = ["Название", "Вилка зарплаты", "Компания", "Город"]
                    
                    vacancy_dict = {}
                    for name, variable in zip(name_list, active_list):
                        
                        try:
                            variable = variable.text
                        except AttributeError:
                            variable = "Неопределён"

                        vacancy_dict[name] = variable
                    vacancy_dict["Ссылка"] = vacancy_link

                    all_list.append(vacancy_dict)

                    print(f'Добавлена вакансия: "{obj_title.text}"')

            print()
            number_list += 1       
        else:
            break

    dump_json(all_list)

if __name__ == "__main__":

    # Точка входа
    main()