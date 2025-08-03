from typing import Any, Generator

import pandas as pd
import pytest
from pandas import DataFrame


# фикстуры к модулю services
# фикстура к функции get_transactions
@pytest.fixture(scope="class")
def df_data() -> Generator[DataFrame, Any, None]:
    """Фикстура: Создает DataFrame с тестовыми данными."""
    # настройка тестовых данных
    data = {
        "Дата платежа": ["2023-10-26", "2023-10-27", "2023-10-28"],
        "Номер карты": ["123456******7890", "987654******3210", "555555******1111"],
        "Категория": ["Продукты", "Развлечения", "Транспорт"],
        "Описание": ["Покупка в супермаркете", "Кинотеатр", "Поездка на такси"],
    }
    df = pd.DataFrame(data)
    # предоставляем DataFrame тестам
    yield df
    # очистка тестовых данных выполнится после завершения всех тестов, использующих фикстуру
    del df


# фикстура к функции get_phone_numbers
@pytest.fixture
def transaction_data() -> list[dict[str, str]]:
    """Фикстура: Предоставляет примеры транзакций для тестов."""
    transactions = [
        {"description": "Оплата заказа +7 900 123-45-67"},
        {"description": "Другая транзакция"},
        {"description": "Пополнение счета +7 912 345-67-89 и еще что-то"},
        {"description": "Просто текст"},
        {"description": "+7 999 888-77-66 в начале строки"},
        {"description": "Текст +79998887766 без пробелов"},  # Не должен быть найден
        {"description": "Текст +8 999 888-77-66 с неправильным кодом страны"},  # Не должен быть найден
        {"неправильная_транзакция": "Текст без description"},  # Пример транзакции без description
    ]
    return transactions
