import os
import json
from datetime import datetime

import pandas as pd
from pandas import DataFrame
import requests
from dotenv import load_dotenv

URL = "https://api.apilayer.com/exchangerates_data/convert"

# Загрузка переменных из .env-файла
load_dotenv()
# импортируем API_KEY из .env-файла
API_KEY_CURRENCY_RATE = os.getenv("API_KEY_CURRENCY_RATE")
API_KEY_STOCKS_RATE = os.getenv("API_KEY_STOCKS_RATE")

def greet():
    """
    Функция, возвращает приветствие в зависимости от времени суток
    """

    current_user_date_time_hour = datetime.now().hour

    if 6 <= current_user_date_time_hour < 12:
        return "Доброе утро"
    elif 12 <= current_user_date_time_hour < 18:
        return "Добрый день"
    elif 18 <= current_user_date_time_hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_date(date_time: str) -> list[str]:
    """
    Функция принимает на вход дату в формате "2020-01-11 16:30:00" и формирует период с начала
    месяца до указанной даты
    """
    # создаем объект datetime из строки
    date_object = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    # создаем начальную дату периода
    first_date_period = date_object.replace(day=1)
    # форматируем периоды в нужный формат
    date_object = date_object.strftime("%d.%m.%Y %H:%M:%S")
    first_date_period = first_date_period.strftime("%d.%m.%Y %H:%M:%S")
    return [first_date_period, date_object]


def read_xlsx(path_to_file_xlsx: str) -> DataFrame:
    """
    Функция принимает путь к файлу Excel и читает его
    """
    excel_data = pd.read_excel(path_to_file_xlsx, sheet_name="Отчет по операциям")
    return excel_data


def get_period(data: DataFrame, date_period: list) -> DataFrame:
    """
    Функция принимает данные из Excel и фильтрует их по указанному периоду, возвращая таблицу
    """
    # преобразовываем данные из столбца "Дата операции" в datetime c параметром dayfirst который
    # указываем на то, что первое число даты это день
    data["Дата операции"] = pd.to_datetime(data["Дата операции"], dayfirst = True)
    # указываем начальную дату
    start_date = date_period[0]
    # указываем конечную дату
    end_date = date_period[1]
    # Преобразуем start_date и end_date в datetime
    start_date = pd.to_datetime(start_date, dayfirst=True)
    end_date = pd.to_datetime(end_date, dayfirst=True)
    # делаем срез по датам
    filtered_data = data[(data["Дата операции"] >= start_date) & (data["Дата операции"] <= end_date)]
    # сортируем по столбцу "Дата операции" от меньшего к большему ascending = True
    sorted_data = filtered_data.sort_values(by="Дата операции", ascending = True)
    return sorted_data

def get_data_cards(data: DataFrame) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает последние 4 цифры карты с общей суммой расходов и кэшбэк по этим картам
    """

    transactions_info = []
    # сортируем данные по необходимым столбцам в последующем по которым будем итерироваться для получения информации
    sorted_info = data[["Номер карты", "Сумма операции", "Кэшбэк", "Сумма операции с округлением"]]

    for index, row in sorted_info.iterrows():
        if row["Сумма операции"] < 0:
            # присваиваем номер карты и форматируем его убирая * впереди
            last_digits = str(row["Номер карты"]).replace("*", "")
            # присваиваем сумму операции
            total_spent = row["Сумма операции с округлением"]
            # присваиваем кэшбэк
            cashback = total_spent // 100
            # создаем необходимый шаблон вывода
            output_template = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback
            }
            transactions_info.append(output_template)
    return transactions_info

def get_top_five(data: DataFrame, top: int) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает top транзакций по сумме платежа
    """

    transactions = []
    # сортируем по столбцу "Сумма операции" от большего к меньшему ascending = False
    sorted_data = data.sort_values(by="Сумма операции", ascending=False)
    # фильтруем данные по первым top с помощью метода .head(top)
    sorted_transactions = sorted_data.head(top)
    # сортируем данные по необходимым столбцам в последующем по которым будем итерироваться для получения информации
    top_transactions_sorted = sorted_transactions [["Дата платежа", "Сумма операции", "Категория", "Описание"]]

    for index, row in top_transactions_sorted.iterrows():
        # создаем необходимый шаблон вывода
        output_template = {
            "date": f"{row["Дата платежа"]}",
            "amount": f"{row["Сумма операции"]}",
            "category": f"{row["Категория"]}",
            "description": f"{row ["Описание"]}"
        }
        transactions.append(output_template)
    return transactions

def get_currency_rate(path_to_file_json: str) -> list[dict]:
    """
    Функция принимает путь к файлу Json и возвращает курс валют
    """
    currency_rate = []
    with open(path_to_file_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        # берем из json файла только валюты
        currencies = data["user_currencies"]

        for currency in currencies:
            # задаем необходимые параметры для запроса
            params = {
                "amount": 1,
                "from": currency,
                "to": "RUB"
            }
            headers = {"apikey": API_KEY_CURRENCY_RATE}
            # формируем ответ
            response = requests.request("GET", URL, headers=headers, params=params)
            # формируем статус код на положительный исход
            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                # берем из ответа валюту из которой переводим в рубли
                currency_response = result["query"]["from"]
                # берем из ответа сумму за 1 рубль и округляем до двух знаков после запятой
                currency_response_amount = round(result["result"], 2)
                # формируем шаблон, который будет добавлять в currency_rate
                currency_rate.append({
                    "currency": currency_response,
                    "rate": currency_response_amount
                })
        return currency_rate

def get_stock_prices(path_to_file_json: str) -> list[dict]:
    """
        Функция принимает путь к файлу Json и возвращает стоимость акций
        """
    stocks_rate = []
    with open(path_to_file_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        # берем из json файла только акции
        stocks = data["user_stocks"]

        for stock in stocks:
            # задаем необходимые параметры для запроса
            symbol = stock
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY_STOCKS_RATE}"
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                # берем из ответа название акции
                stock_response = result["Global Quote"]["01. symbol"]
                # берем из ответа стоимость акции
                stock_response_price = result["Global Quote"]["05. price"]
                # формируем шаблон, который будет добавлять в stocks_rate
                stocks_rate.append({
                    "stock": stock_response,
                    "price": stock_response_price
                })
        return stocks_rate
