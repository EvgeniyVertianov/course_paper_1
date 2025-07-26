import json

from src.utils import get_phone_numbers, get_transactions, read_xlsx


def main_services() -> str:
    """
    Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера
    """
    # Подготовка данных к работе
    get_data = read_xlsx("../data/operations.xlsx")

    # основное тело кода
    transactions = get_transactions(get_data)
    phone_numbers = get_phone_numbers(transactions)

    # преобразовываем transactions в JSON сроку с форматированием отступов в 4 пробела indent=4
    json_data = json.dumps(phone_numbers, ensure_ascii=False, indent=4)

    return json_data
