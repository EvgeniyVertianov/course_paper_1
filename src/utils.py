import logging
import os
import json
from datetime import datetime

import pandas as pd
from pandas import DataFrame
import requests
from dotenv import load_dotenv

# настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# получаем логгер для текущего модуля
logger = logging.getLogger(__name__)

URL = "https://api.apilayer.com/exchangerates_data/convert"

# Загрузка переменных из .env-файла
load_dotenv()
# импортируем API_KEY из .env-файла
API_KEY_CURRENCY_RATE = os.getenv("API_KEY_CURRENCY_RATE")
API_KEY_STOCKS_RATE = os.getenv("API_KEY_STOCKS_RATE")


def greet(date_time: datetime = None) -> str:
    """
    Функция, возвращает приветствие в зависимости от времени суток.
    Добавлено логирование и обработка потенциальных ошибок.
    """
    logger.info("Начало работы функции greet.")

    try:
        if date_time is None:
            current_user_date_time_hour = datetime.now().hour
        elif not isinstance(date_time, datetime):  # Проверка типа
            logger.error("Передан неверный тип данных. Ожидается datetime.")
            return "Неверный формат даты"
        else:
            current_user_date_time_hour = date_time.hour
        logger.debug(f"Текущий час: {current_user_date_time_hour}.")

        if 6 <= current_user_date_time_hour < 12:
            greeting = "Доброе утро"
        elif 12 <= current_user_date_time_hour < 18:
            greeting = "Добрый день"
        elif 18 <= current_user_date_time_hour < 22:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        logger.info(f"Приветствие сформировано: {greeting}.")
        return greeting

    except Exception as e:
        logger.error(f"В функции greet произошла ошибка: {e}.")
        return "Неверный формат даты"

    finally:
        # всегда выполняется, даже при ошибке
        logger.info("Функция greet завершила выполнение.")


def get_date(date_time: str) -> list[str]:
    """
    Функция принимает на вход дату в формате "2020-01-11 16:30:00" и формирует период с начала
    месяца до указанной даты
    """
    logging.info(f"Начало работы функции get_date: {date_time}.")
    try:
        # создаем объект datetime из строки
        date_object = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        logging.debug(f"Объект преобразован в datetime: {date_object}.")

        # создаем начальную дату периода
        first_date_period = date_object.replace(day=1)
        logging.debug(f"Первая дата периода создана: {first_date_period}.")

        # форматируем периоды в нужный формат
        date_object = date_object.strftime("%d.%m.%Y %H:%M:%S")
        first_date_period = first_date_period.strftime("%d.%m.%Y %H:%M:%S")
        logging.debug(f"Отформатированная дата: {date_object}.")
        logging.debug(f"Отформатированная первая дата периода: {first_date_period}.")

        result = [first_date_period, date_object]
        logging.info(f"Функция get_date успешно завершена. Результат: {result}.")
        return result

    except ValueError as e:
        logging.error(f"Ошибка ValueError: {e}. Некорректный формат даты: {date_time}.")
        return []

    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}.")
        return []


def read_xlsx(path_to_file_xlsx: str) -> DataFrame:
    """
    Функция принимает путь к файлу Excel и читает его
    """
    logging.info(f"Начало работы функции read_xlsx: {path_to_file_xlsx}.")

    try:
        excel_data = pd.read_excel(path_to_file_xlsx, sheet_name="Отчет по операциям")
        logging.debug(f"Файл успешно прочитан. Форма DataFrame: {excel_data.shape}.")
        logging.info(f"Функция read_xlsx успешно завершена.")
        return excel_data

    except FileNotFoundError:
        logging.error(f"Файл не найден: {path_to_file_xlsx}.")
        return pd.DataFrame()

    except pd.errors.ParserError as e:
        logging.error(f"Ошибка при парсинге Excel файла: {e}.")
        return pd.DataFrame()

    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}.")
        return pd.DataFrame()


def get_period(data: DataFrame, date_period: list) -> DataFrame:
    """
    Функция принимает данные из Excel и фильтрует их по указанному периоду, возвращая таблицу
    """
    logging.info("Начало выполнения функции get_period.")
    logging.debug(
        f"Входные параметры: data (форма DataFrame с {data.shape[0]} строк и {data.shape[1]} столбцов), date_period={date_period}.")

    try:
        logging.info("Преобразование столбца 'Дата операции' в datetime.")
        # преобразовываем данные из столбца "Дата операции" в datetime c параметром dayfirst который
        # указываем на то, что первое число даты это день
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], dayfirst=True)
        logging.debug(f"Тип данных столбца 'Дата операции' после преобразования: {data['Дата операции'].dtype}.")

        # указываем начальную дату
        start_date = date_period[0]
        # указываем конечную дату
        end_date = date_period[1]
        logging.debug(f"Начальная дата: {start_date}, Конечная дата: {end_date}.")

        # Преобразуем start_date и end_date в datetime
        logging.info("Преобразование start_date и end_date в datetime.")
        start_date = pd.to_datetime(start_date, dayfirst=True)
        end_date = pd.to_datetime(end_date, dayfirst=True)
        logging.debug(f"start_date после преобразования: {start_date}, end_date после преобразования: {end_date}.")

        # делаем срез по датам
        logging.info("Фильтрация данных по периоду.")
        filtered_data = data[(data["Дата операции"] >= start_date) & (data["Дата операции"] <= end_date)]
        logging.debug(f"Количество строк после фильтрации: {filtered_data.shape[0]}.")

        # сортируем по столбцу "Дата операции" от меньшего к большему ascending = True
        logging.info("Сортировка данных по столбцу 'Дата операции'.")
        sorted_data = filtered_data.sort_values(by="Дата операции", ascending=True)
        logging.debug("Данные отсортированы.")

        logging.info("Функция get_period успешно выполнена.")
        return sorted_data

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}", exc_info=True)
        raise


def get_data_cards(data: DataFrame) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает последние 4 цифры карты с общей суммой расходов и кэшбэк по этим картам
    """

    logging.info("Начало обработки данных для получения информации о картах.")

    transactions_info = []
    # сортируем данные по необходимым столбцам в последующем по которым будем итерироваться для получения информации
    sorted_info = data[["Номер карты", "Сумма операции", "Кэшбэк", "Сумма операции с округлением"]]
    # Логируем первые 5 строк для проверки
    logging.debug(f"Первые 5 строк отсортированных данных:\n{sorted_info.head()}.")

    for index, row in sorted_info.iterrows():
        try:
            if row["Сумма операции"] < 0:
                # присваиваем номер карты и форматируем его убирая * впереди
                last_digits = str(row["Номер карты"]).replace("*", "")
                # присваиваем сумму операции
                total_spent = row["Сумма операции с округлением"]
                # присваиваем кэшбэк
                cashback = round((total_spent / 100), 2)
                # создаем необходимый шаблон вывода
                output_template = {
                    "last_digits": last_digits,
                    "total_spent": total_spent,
                    "cashback": cashback
                }
                transactions_info.append(output_template)
                logging.debug(f"Обработана транзакция для карты с последними цифрами: {last_digits}. "
                              f"Сумма: {total_spent}, Кэшбэк: {cashback}.")
        except KeyError as e:
            logging.error(f"Ошибка KeyError: Отсутствует столбец {e} в DataFrame.")
            return []
        except Exception as e:
            logging.error(f"Произошла ошибка при обработке строки {index}: {e}.")
            return []

    logging.info(f"Обработано {len(transactions_info)} транзакций.")
    logging.info("Завершение обработки данных о картах.")
    return transactions_info

def get_top_five(data: DataFrame, top: int) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает top транзакций по сумме платежа
    """

    logging.info(f"Начало поиска топ {top} транзакций.")

    transactions = []
    try:
        # сортируем по столбцу "Сумма операции" от большего к меньшему ascending = False
        logging.debug("Сортировка данных по сумме операции.")
        sorted_data = data.sort_values(by="Сумма операции", ascending=False)

        # фильтруем данные по первым top с помощью метода .head(top)
        logging.debug(f"Выборка топ {top} транзакций.")
        sorted_transactions = sorted_data.head(top)

        # сортируем данные по необходимым столбцам в последующем по которым будем итерироваться для получения информации
        logging.debug("Выбор необходимых столбцов.")
        top_transactions_sorted = sorted_transactions[["Дата платежа", "Сумма операции", "Категория", "Описание"]]
        logging.debug(f"Первые {top} строк отсортированных данных:\n{top_transactions_sorted.head()}.")

        logging.debug("Итерация по транзакциям и создание шаблона вывода.")
        for index, row in top_transactions_sorted.iterrows():
            # создаем необходимый шаблон вывода
            output_template = {
                "date": str(row["Дата платежа"]),
                "amount": str(row["Сумма операции"]),
                "category": str(row["Категория"]),
                "description": str(row["Описание"])
            }
            transactions.append(output_template)
            logging.debug(f"Транзакция обработана: {output_template}")

        logging.info(f"Найдено {len(transactions)} топ транзакций.")
        return transactions

    except KeyError as e:
        logging.error(f"Ошибка KeyError: Отсутствует столбец {e} в DataFrame.")
        return []
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке данных: {e}")
        return []
    finally:
        logging.info("Завершение поиска топ транзакций.")

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
