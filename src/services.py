import json

import pandas as pd

from src.utils import get_phone_numbers, get_transactions


def main_services(data: pd.DataFrame) -> str:
    """
    Функция принимает DataFrame и возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера
    """

    # основное тело кода
    transactions = get_transactions(data)
    phone_numbers = get_phone_numbers(transactions)

    # преобразовываем transactions в JSON сроку с форматированием отступов в 4 пробела indent=4
    json_data = json.dumps(phone_numbers, ensure_ascii=False, indent=4)

    return json_data
