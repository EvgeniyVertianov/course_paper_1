import json

from src.utils import (get_currency_rate, get_data_cards, get_date, get_period, get_stock_prices, get_top_five, greet,
                       read_xlsx)


def main_views(date_time: str) -> str:
    """
    Функция, принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращает JSON-ответ c данными с начала месяца, на который выпадает входящая дата, по входящую дату.
    Например: Если указана дата 20.05.2020, то данные для анализа будут в диапазоне 01.05.2020-20.05.2020.
    """
    # Подготовка данных к работе по диапазону дат
    date_period = get_date(date_time)
    get_data = read_xlsx("../data/operations.xlsx")
    get_data_filtered = get_period(get_data, date_period)

    # Задание 1 - Приветствие
    greeting = greet(date_time)

    # Задание 2 - По каждой карте
    data_cards = get_data_cards(get_data_filtered)

    # Задание 3 - Топ-5 транзакций по сумме платежа
    top_five_transactions = get_top_five(get_data_filtered, 5)

    # Задание 4 - Курс валют
    currency_rate = get_currency_rate("../data/user_settings.json")

    # Задание 5 - Стоимость акций из S&P500
    stock_prices = get_stock_prices("../data/user_settings.json")

    data = {
        "greeting": greeting,
        "cards": data_cards,
        "top_transactions": top_five_transactions,
        "currency_rates": currency_rate,
        "stock_prices": stock_prices,
    }
    # преобразовываем data в JSON сроку с форматированием отступов в 4 пробела indent=4
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data
