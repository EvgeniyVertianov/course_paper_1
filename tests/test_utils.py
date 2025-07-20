import unittest
from datetime import datetime
import os
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
import requests

from src.utils import greet, get_date


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

# тест на функцию get_date
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