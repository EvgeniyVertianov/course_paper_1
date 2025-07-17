from src.utils import greet, get_date, read_xlsx, get_period


def main_views(date_time: str) -> str:
    """
    Функция, принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращает JSON-ответ, пример 2025-01-11 16:30:00
    """

    greeting = greet()
    date_period = get_date(date_time)
    get_data = read_xlsx("../data/operations.xlsx")
    get_data_filtered = get_period(get_data, date_period)
    return greeting, get_data_filtered