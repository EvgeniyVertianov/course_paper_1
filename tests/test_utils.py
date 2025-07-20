import unittest
import pandas as pd
from pandas import DataFrame
from datetime import datetime
import os
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
import requests

from src.utils import greet, get_date, read_xlsx, get_period


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