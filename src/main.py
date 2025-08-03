from typing import Any

from src.reports import spending_by_category
from src.services import main_services
from src.utils import read_xlsx
from src.views import main_views


def choose_filtered_category(date: str) -> Any:
    """
    Функция предлагает фильтрацию трат по категории за последние три месяца (от указанной даты).
    """
    while True:
        question = input(
            "Проанализировать траты по категории за последние три месяца (от указанной даты)?. Да/Нет: "
        ).lower()
        format_date = f"{date[8:10]}.{date[5:7]}.{date[:4]}"
        get_dataframe = read_xlsx("../data/operations.xlsx")
        if question == "да":
            category_name = input("Введите категорию трат для анализа: ").title()
            result = spending_by_category(get_dataframe, category_name, format_date)
            return result
        elif question == "нет":
            break
        else:
            print("Введите корректное значение ('Да' или 'Нет').")
    return None


def choose_filtered_phone() -> str | None:
    """
    Функция предлагает фильтрацию по наличию в описании транзакций номеров сотовых телефонов.
    """
    while True:
        question = input("Вывести транзакции в описании которых есть номера сотовых телефонов?. Да/Нет: ").lower()
        get_dataframe = read_xlsx("../data/operations.xlsx")
        if question == "да":
            result = main_services(get_dataframe)
            return result
        elif question == "нет":
            break
        else:
            print("Введите корректное значение ('Да' или 'Нет').")
    return None


def main() -> Any:
    """Основная функция запускающая весь проект"""
    date = input(
        "Введите дату в формате YYYY-MM-DD HH:MM:SS (пример: 2021-12-30 20:00:00) для вывода основной информации\n"
        "по картам с начала месяца указанной даты: "
    )
    print(main_views(date))
    print(choose_filtered_category(date))
    print(choose_filtered_phone())


if __name__ == "__main__":
    print(main())
