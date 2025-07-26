from typing import Any

import pandas as pd

from src.utils import get_phone_numbers, get_transactions


class TestGetTransactions:
    """Тесты для функции get_transactions"""

    def test_get_transactions_success(self, df_data: Any) -> None:
        """Тест: Функция успешно извлекает транзакции из DataFrame"""
        expected_transactions = [
            {
                "payment date": "2023-10-26",
                "card number": "123456******7890",
                "category": "Продукты",
                "description": "Покупка в супермаркете",
            },
            {
                "payment date": "2023-10-27",
                "card number": "987654******3210",
                "category": "Развлечения",
                "description": "Кинотеатр",
            },
            {
                "payment date": "2023-10-28",
                "card number": "555555******1111",
                "category": "Транспорт",
                "description": "Поездка на такси",
            },
        ]

        transactions = get_transactions(df_data)
        assert transactions == expected_transactions

    def test_get_transactions_empty_dataframe(self) -> None:
        """Тест: Функция возвращает пустой список для пустого DataFrame"""
        df = pd.DataFrame()
        transactions = get_transactions(df)
        assert transactions == []

    def test_get_transactions_missing_column(self) -> None:
        """Тест: Функция возвращает пустой список, если отсутствует один из столбцов"""
        data = {"Дата платежа": ["2023-10-26"], "Номер карты": ["123456******7890"], "Категория": ["Продукты"]}
        df = pd.DataFrame(data)

        transactions = get_transactions(df)
        assert transactions == []

    def test_get_transactions_different_data_types(self) -> None:
        """Тест: Функция корректно обрабатывает DataFrame с разными типами данных"""
        data = {
            "Дата платежа": [pd.Timestamp("2023-10-26")],
            "Номер карты": [1234567890],
            "Категория": ["Продукты"],
            "Описание": [123.45],
        }

        df = pd.DataFrame(data)

        expected_transactions = [
            {
                "payment date": "2023-10-26 00:00:00",
                "card number": "1234567890",
                "category": "Продукты",
                "description": "123.45",
            }
        ]

        transactions = get_transactions(df)
        assert transactions == expected_transactions


# тесты для функции get_phone_numbers
def test_get_phone_numbers_success(transaction_data: list) -> None:
    """Тест: Функция успешно извлекает транзакции с номерами телефонов."""
    expected_transactions = [
        {"description": "Оплата заказа +7 900 123-45-67"},
        {"description": "Пополнение счета +7 912 345-67-89 и еще что-то"},
        {"description": "+7 999 888-77-66 в начале строки"},
    ]

    result = get_phone_numbers(transaction_data)
    assert result == expected_transactions


def test_get_phone_numbers_no_phone_numbers(transaction_data: list) -> None:
    """Тест: Функция возвращает пустой список, если нет номеров телефонов."""
    transactions = [
        {"description": "Другая транзакция"},
        {"description": "Просто текст"},
        {"неправильная_транзакция": "Текст без description"},
    ]

    result = get_phone_numbers(transactions)
    assert result == []


def test_get_phone_numbers_empty_list() -> None:
    """Тест: Функция возвращает пустой список, если на вход дан пустой список."""
    result = get_phone_numbers([])
    assert result == []


def test_get_phone_numbers_missing_description(transaction_data: list) -> None:
    """Тест: Функция корректно обрабатывает транзакции без поля 'description'."""
    transactions = [
        {"неправильная_транзакция": "Текст без description"}
    ]  # Заменяем transaction_data одним элементом для теста
    result = get_phone_numbers(transactions)
    assert result == []


def test_get_phone_numbers_invalid_format(transaction_data: list) -> None:
    """Тест: Функция не находит номера в неправильном формате."""
    transactions = [
        {"description": "Текст +79998887766 без пробелов"},  # Не должен быть найден
        {"description": "Текст +8 999 888-77-66 с неправильным кодом страны"},  # Не должен быть найден
    ]
    result = get_phone_numbers(transactions)
    assert result == []
