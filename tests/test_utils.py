import unittest
from unittest.mock import patch, mock_open
import json
from pandas import DataFrame
from datetime import datetime
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv

import numpy as np
import pandas as pd
import pytest
import requests

from src.utils import greet, get_date, read_xlsx, get_period, get_data_cards, get_top_five, get_currency_rate



# тест на функцию greet
@pytest.mark.parametrize(
    "date_obj, expected",
    [
        (datetime(2024, 1, 1, 1, 0, 0), "Доброй ночи"),
        (datetime(2024, 1, 1, 7, 0, 0), "Доброе утро"),
        (datetime(2024, 1, 1, 13, 0, 0), "Добрый день"),
        (datetime(2024, 1, 1, 20, 0, 0), "Добрый вечер"),
        ("31.12.2021", "Неверный формат даты"),
    ],
)
def test_greet_correct(date_obj: datetime, expected: str) -> None:
    assert greet(date_obj) == expected

# тесты на функцию get_date
class TestGetDate(unittest.TestCase):

    def test_valid_date(self):
        """Тест проверяет функцию с корректной датой"""
        date_time = "2020-01-11 16:30:00"
        expected_result = ["01.01.2020 16:30:00", "11.01.2020 16:30:00"]
        actual_result = get_date(date_time)
        self.assertEqual(actual_result, expected_result)

    def test_different_year_and_month(self):
        """Тест проверяет функцию с датой из другого года и месяца"""
        date_time = "2023-12-25 08:00:00"
        expected_result = ["01.12.2023 08:00:00", "25.12.2023 08:00:00"]
        actual_result = get_date(date_time)
        self.assertEqual(actual_result, expected_result)

    def test_invalid_date_format(self):
        """Тест проверяет функцию с некорректным форматом даты"""
        date_time = "2020-01-11"
        expected_result = []
        actual_result = get_date(date_time)
        self.assertEqual(actual_result, expected_result)

    def test_empty_date(self):
        """Тест проверяет функцию с пустой датой"""
        date_time = ""
        expected_result = []
        actual_result = get_date(date_time)
        self.assertEqual(actual_result, expected_result)

    def test_invalid_characters(self):
        """Тест проверяет функцию с датой, содержащей некорректные символы"""
        date_time = "2020-AA-BB 16:30:00"
        expected_result = []
        actual_result = get_date(date_time)
        self.assertEqual(actual_result, expected_result)

    def test_leap_year(self):
        """Тест проверяет функцию с датой в високосном году"""
        date_time = "2024-02-29 12:00:00"
        expected_result = ["01.02.2024 12:00:00", "29.02.2024 12:00:00"]
        actual_result = get_date(date_time)
        self.assertEqual(actual_result, expected_result)

# тесты на функцию read_xlsx
class TestReadXlsx(unittest.TestCase):

    def setUp(self):
        """Тест создает тестовый Excel-файл перед каждым тестом"""
        self.test_file = "test_excel.xlsx"
        self.sheet_name = "Отчет по операциям"
        # пример данных для записи
        self.data = {'col1': [1, 2], 'col2': [3, 4]}
        self.df = pd.DataFrame(self.data)
        self.df.to_excel(self.test_file, sheet_name=self.sheet_name, index=False)

    def tearDown(self):
        """Тест удаляет тестовый Excel-файл после каждого теста"""
        try:
            os.remove(self.test_file)
        except FileNotFoundError:
            # файл мог быть не создан, если тест не удался
            pass

    def test_valid_file(self):
        """Тест проверяет чтение существующего файла"""
        result_df = read_xlsx(self.test_file)
        # проверяем, что вернулся DataFrame
        self.assertIsInstance(result_df, DataFrame)
        # проверяем, что DataFrame не пустой
        self.assertFalse(result_df.empty)
        # сравниваем DataFrame с ожидаемым
        pd.testing.assert_frame_equal(result_df, self.df)

    def test_file_not_found(self):
        """Тест проверяет обработку несуществующего файла"""
        result_df = read_xlsx("non_existent_file.xlsx")
        # проверяем, что вернулся DataFrame
        self.assertIsInstance(result_df, DataFrame)
        # проверяем, что DataFrame пустой
        self.assertTrue(result_df.empty)

    def test_invalid_file(self):
        """Тест проверяет обработку поврежденного или не-Excel файла"""
        with open("invalid_file.txt", "w") as f:
            f.write("This is not an Excel file.")

        result_df = read_xlsx("invalid_file.txt")
        self.assertIsInstance(result_df, DataFrame)
        self.assertTrue(result_df.empty)
        os.remove("invalid_file.txt")

    def test_empty_file(self):
        """Тест проверяет чтение пустого excel файла"""
        empty_test_file = "empty_test_excel.xlsx"
        empty_df = pd.DataFrame()
        # создаем пустой excel файл
        empty_df.to_excel(empty_test_file, sheet_name=self.sheet_name, index=False)

        result_df = read_xlsx(empty_test_file)

        self.assertIsInstance(result_df, DataFrame)
        # результатом должен быть пустой DataFrame
        self.assertTrue(result_df.empty)

        os.remove(empty_test_file)

# тесты на функцию get_period
class TestGetPeriod(unittest.TestCase):

    def test_empty_dataframe(self):
        """Тест с пустым DataFrame"""
        data = pd.DataFrame({'Дата операции': []})
        date_period = ['01.01.2023', '31.01.2023']
        result = get_period(data, date_period)
        # Проверяем, что результат - пустой DataFrame
        self.assertTrue(result.empty)

    def test_valid_period(self):
        """Тест с валидным периодом"""
        data = pd.DataFrame({
            'Дата операции': ['05.01.2023', '10.01.2023', '15.01.2023', '20.01.2023'],
            'Сумма': [100, 200, 300, 400]
        })
        date_period = ['01.01.2023', '15.01.2023']
        result = get_period(data, date_period)
        # Проверяем количество строк
        self.assertEqual(len(result), 3)
        # Проверяем правильность фильтрации
        self.assertEqual(result['Сумма'].sum(), 600)

    def test_period_outside_data_range(self):
        """Тест, когда период выходит за пределы данных"""
        data = pd.DataFrame({
            'Дата операции': ['05.01.2023', '10.01.2023', '15.01.2023'],
            'Сумма': [100, 200, 300]
        })
        # Период после имеющихся данных
        date_period = ['01.02.2023', '28.02.2023']
        result = get_period(data, date_period)
        # Должен вернуться пустой DataFrame
        self.assertTrue(result.empty)

    def test_incorrect_date_format_in_data(self):
        """Тест с некорректным форматом даты в данных"""
        data = pd.DataFrame({
            'Дата операции': ['05-01-2023', '10.01.2023'],
            'Сумма': [100, 200]
        })
        date_period = ['01.01.2023', '15.01.2023']
        # Ожидаем ошибку преобразования даты
        with self.assertRaises(ValueError):
            get_period(data, date_period)

    def test_date_period_with_time(self):
        """Тест с датами, содержащими время"""
        data = pd.DataFrame({
            'Дата операции': ['05.01.2023 10:00', '10.01.2023 12:00'],
            'Сумма': [100, 200]
        })
        date_period = ['01.01.2023', '15.01.2023']
        result = get_period(data, date_period)
        # Обе даты должны попасть в период
        self.assertEqual(len(result), 2)

    def test_already_sorted_data(self):
         """Тест с уже отсортированными данными, чтобы проверить, что сортировка не ломает порядок"""
         data = pd.DataFrame({
            'Дата операции': ['01.01.2023', '05.01.2023', '10.01.2023'],
            'Сумма': [100, 200, 300]
        })
         data['Дата операции'] = pd.to_datetime(data['Дата операции'], dayfirst=True)
         date_period = ['01.01.2023', '15.01.2023']
         # Важно: data.copy(), чтобы не менять исходный DataFrame
         result = get_period(data.copy(), date_period)
         # Проверяем, что порядок не нарушен
         self.assertTrue(result['Дата операции'].is_monotonic_increasing)

# тесты на функцию get_data_cards

class TestGetDataCards(unittest.TestCase):

    def test_empty_dataframe(self):
        """Тест с пустым DataFrame"""
        data = pd.DataFrame({
            "Номер карты": [],
            "Сумма операции": [],
            "Кэшбэк": [],
            "Сумма операции с округлением": []
        })
        result = get_data_cards(data)
        self.assertEqual(result, [])

    def test_valid_transactions(self):
        """Тест с валидными транзакциями"""
        data = pd.DataFrame({
            "Номер карты": ["*1234", "*5678"],
            "Сумма операции": [-100, -250],
            "Кэшбэк": [1, 2],
            "Сумма операции с округлением": [-100.0, -250.0]
        })
        expected_result = [
            {"last_digits": "1234", "total_spent": -100.0, "cashback": -1.0},
            {"last_digits": "5678", "total_spent": -250.0, "cashback": -2.5}
        ]
        result = get_data_cards(data)
        self.assertEqual(result, expected_result)

    def test_no_negative_transactions(self):
        """Тест, когда нет отрицательных транзакций"""
        data = pd.DataFrame({
            "Номер карты": ["*1234", "*5678"],
            "Сумма операции": [100, 200],
            "Кэшбэк": [0, 0],
            "Сумма операции с округлением": [100, 200]
        })
        result = get_data_cards(data)
        self.assertEqual(result, [])

# тесты на функцию get_top_five

class TestGetTopFive(unittest.TestCase):

    def test_empty_dataframe(self):
        """Тест с пустым DataFrame"""
        data = pd.DataFrame({
                "Дата платежа": [],
                "Сумма операции": [],
                "Категория": [],
                "Описание": []
            })
        result = get_top_five(data, 3)
        self.assertEqual(result, [])

    def test_valid_transactions(self):
        """Тест с валидными транзакциями"""
        data = pd.DataFrame({
            "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
            "Сумма операции": [100, 200, 50, 300],
            "Категория": ["A", "B", "C", "D"],
            "Описание": ["Desc1", "Desc2", "Desc3", "Desc4"]
        })
        expected_result = [
            {"date": "2023-01-04", "amount": "300", "category": "D", "description": "Desc4"},
            {"date": "2023-01-02", "amount": "200", "category": "B", "description": "Desc2"},
            {"date": "2023-01-01", "amount": "100", "category": "A", "description": "Desc1"}
        ]
        result = get_top_five(data, 3)
        self.assertEqual(result, expected_result)

    def test_fewer_transactions_than_top(self):
        """Тест, когда транзакций меньше, чем запрошенный топ"""
        data = pd.DataFrame({
            "Дата платежа": ["2023-01-01", "2023-01-02"],
            "Сумма операции": [100, 200],
            "Категория": ["A", "B"],
            "Описание": ["Desc1", "Desc2"]
        })
        expected_result = [
            {"date": "2023-01-02", "amount": "200", "category": "B", "description": "Desc2"},
            {"date": "2023-01-01", "amount": "100", "category": "A", "description": "Desc1"}
        ]
        result = get_top_five(data, 5)
        self.assertEqual(result, expected_result)

    def test_key_error(self):
        """Тест, когда в DataFrame отсутствует необходимый столбец"""
        data = pd.DataFrame({
            "Неправильный столбец": ["2023-01-01"],
        })
        result = get_top_five(data, 1)
        self.assertEqual(result, [])

# тесты на функцию get_currency_rate

class TestGetCurrencyRate(unittest.TestCase):

    @patch('src.utils.requests.request')
    def test_successful_currency_retrieval(self, mock_request):
        """Тест успешного получения курса валют"""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {"from": "USD"},
            "result": 75.50
        }
        mock_request.return_value = mock_response

        mock_file_content = json.dumps({"user_currencies": ["USD"]})
        with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
            result = get_currency_rate("dummy_path.json")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rate"], 75.50)

    @patch('src.utils.requests.request')
    def test_api_error(self, mock_request):
        """Тест обработки ошибки API"""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response

        mock_file_content = json.dumps({"user_currencies": ["USD"]})
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_currency_rate("dummy_path.json")

        self.assertEqual(len(result), 0)

    def test_file_not_found(self):
        """Тест обработки ошибки, когда файл не найден"""
        result = get_currency_rate("nonexistent_file.json")
        self.assertEqual(len(result), 0)

    def test_invalid_json(self):
        """Тест обработки ошибки, когда JSON в файле некорректный"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = get_currency_rate("dummy_path.json")
        self.assertEqual(len(result), 0)

    def test_missing_user_currencies_key(self):
        """Тест обработки ошибки, когда отсутствует ключ 'user_currencies'"""
        mock_file_content = json.dumps({"other_key": ["USD"]})
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_currency_rate("dummy_path.json")
        self.assertEqual(len(result), 0)

    @patch('src.utils.requests.request', side_effect=requests.exceptions.RequestException("Test Exception")) # замените your_module
    def test_request_exception(self, mock_request):
         """Тест обработки исключения requests"""
         mock_file_content = json.dumps({"user_currencies": ["USD"]})
         with patch("builtins.open", mock_open(read_data=mock_file_content)):
              result = get_currency_rate("dummy_path.json")
         self.assertEqual(len(result), 0)