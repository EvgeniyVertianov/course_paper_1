from datetime import datetime

import pandas as pd
from pandas import DataFrame

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


def read_xlsx(path_to_file: str) -> DataFrame:
    """
    Функция принимает путь к файлу Excel и читает его
    """
    excel_data = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")
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
    # сортируем по возрастанию
    sorted_data = filtered_data.sort_values(by="Дата операции", ascending = True)
    return sorted_data
