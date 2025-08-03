import json
import os
import unittest
from typing import Any

import pandas as pd

from src.reports import decorator, spending_by_category


# тесты для декоратора
class TestDecorator(unittest.TestCase):

    def setUp(self) -> None:
        # убедимся, что тестовые файлы не существуют перед началом каждого теста
        self.default_filename = "my_function_report.txt"
        self.custom_filename = "custom_report.txt"
        for filename in [self.default_filename, self.custom_filename]:
            if os.path.exists(filename):
                os.remove(filename)

    def tearDown(self) -> None:
        # удалим тестовые файлы после каждого теста
        for filename in [self.default_filename, self.custom_filename]:
            if os.path.exists(filename):
                os.remove(filename)

    def test_decorator_with_default_filename(self) -> None:
        @decorator()
        def my_function(x: int) -> int:
            return x * 2

        result = my_function(5)
        self.assertEqual(result, 10)
        self.assertTrue(os.path.exists(self.default_filename))
        with open(self.default_filename, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "10")

    def test_decorator_with_custom_filename(self) -> None:
        @decorator(filename="custom_report.txt")
        def my_function(x: int) -> int:
            return x * 2

        result = my_function(5)
        self.assertEqual(result, 10)
        self.assertTrue(os.path.exists(self.custom_filename))
        with open(self.custom_filename, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "10")

    def test_decorator_with_dataframe(self) -> None:
        @decorator()
        def my_dataframe_function() -> Any:
            data = {"col1": [1, 2], "col2": [3, 4]}
            df = pd.DataFrame(data)
            return df

        result = my_dataframe_function()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(os.path.exists("my_dataframe_function_report.txt"))
        with open("my_dataframe_function_report.txt", "r", encoding="utf-8") as f:
            content = f.read()
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        expected_json = df.to_json(orient="records", indent=4, force_ascii=False)
        content = content.replace(": ", ":")
        self.assertEqual(content, expected_json)

    def test_decorator_preserves_function_name(self) -> None:
        @decorator()
        def my_function(x: int) -> int:
            """Докстринги к моей функции"""
            return x * 2

        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "Докстринги к моей функции")

    def test_decorator_no_args_kwargs(self) -> None:
        @decorator()
        def my_function() -> str:
            return "Hello"

        result = my_function()
        self.assertEqual(result, "Hello")
        self.assertTrue(os.path.exists("my_function_report.txt"))
        with open("my_function_report.txt", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "Hello")


# тесты для функции spending_by_category


class TestSpendingByCategory(unittest.TestCase):
    def setUp(self) -> None:
        # настройка: создаем пример DataFrame транзакций
        self.transactions_data = {
            "Дата платежа": [
                "01.01.2024",
                "15.02.2024",
                "20.03.2024",
                "31.12.2023",
                "10.10.2023",
            ],
            "Категория": [
                "Еда",
                "Транспорт",
                "Еда",
                "Еда",
                "Развлечения",
            ],
            "Сумма": [100, 200, 150, 50, 75],
        }
        self.transactions = pd.DataFrame(self.transactions_data)
        self.category = "Еда"
        self.report_file = "spending_by_category_report.txt"

        # очищаем все оставшиеся файлы отчетов от предыдущих запусков
        if os.path.exists(self.report_file):
            os.remove(self.report_file)

    def tearDown(self) -> None:
        # очистка: удаляем файл отчета после каждого теста
        if os.path.exists(self.report_file):
            os.remove(self.report_file)

    def test_spending_by_category_with_date(self) -> None:
        @decorator()
        def spending_by_category_test(transactions: Any, category: Any, date: Any = None) -> Any:
            return spending_by_category(transactions, category, date)

        date_str = "31.03.2024"
        result = spending_by_category_test(self.transactions.copy(), self.category, date_str)
        # проверяем, создан ли файл
        self.assertTrue(os.path.exists(self.report_file))
        expected_data = [
            {"Дата платежа": "01.01.2024", "Категория": "Еда", "Сумма": 100},
            {"Дата платежа": "20.03.2024", "Категория": "Еда", "Сумма": 150},
            {"Дата платежа": "31.12.2023", "Категория": "Еда", "Сумма": 50},
        ]
        expected_data = [item for item in expected_data if item["Дата платежа"] != "31.12.2023"]
        expected_json = json.dumps(expected_data, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(result, expected_json)

    def test_spending_by_category_no_matching_category(self) -> None:
        @decorator()
        def spending_by_category_test(transactions: Any, category: Any, date: Any = None) -> Any:
            return spending_by_category(transactions, category, date)

        non_existent_category = "Одежда"
        result = spending_by_category_test(self.transactions.copy(), non_existent_category)
        expected_json = json.dumps([], ensure_ascii=False)
        self.assertEqual(result, expected_json)

    def test_date_format_error(self) -> None:
        @decorator()
        def spending_by_category_test(transactions: Any, category: Any, date: Any = None) -> Any:
            return spending_by_category(transactions, category, date)

        # неправильные данные: неверный формат даты
        bad_transactions_data = {
            "Дата платежа": ["01-01-2024"],
            "Категория": ["Еда"],
            "Сумма": [100],
        }
        bad_transactions = pd.DataFrame(bad_transactions_data)
        with self.assertRaisesRegex(ValueError, "Не удалось определить формат даты в столбце."):
            spending_by_category_test(bad_transactions, "Еда")
