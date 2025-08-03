import datetime
import logging
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def decorator(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования функций и вывода результатов в файл. Принимает на вход необязательный аргумент filename.
    Если filename не указан, используется имя функции с суффиксом "_report.txt".
    """

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"Вызов функции: {func.__name__} с аргументами: {args}, {kwargs}.")

            output_filename = filename if filename else f"{func.__name__}_report.txt"

            try:
                result = func(*args, **kwargs)
                with open(output_filename, "w", encoding="utf-8") as file:
                    if isinstance(result, pd.DataFrame):
                        result.to_json(file, index=False, force_ascii=False, orient="records", indent=4)
                        logger.info(f"Данные успешно записаны в файл: {output_filename}.")
                    else:
                        file.write(str(result))
                        logger.info(f"Данные успешно записаны в файл: {output_filename}.")
                return result

            except Exception as error:
                logger.exception(f"В работе функции {func.__name__} возникла ошибка: {error}.")
                with open(output_filename, "w", encoding="utf-8") as file:
                    file.write(f"Error in {func.__name__}: {error}. Inputs: {args}, {kwargs}.")
                raise

        return inner

    return wrapper


@decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
    Функция принимает DataFrame и возвращает траты по заданной категории за последние три месяца (от переданной даты)
    """

    if date:
        end_date = datetime.datetime.strptime(date, "%d.%m.%Y")
    else:
        end_date = datetime.datetime.now()

    start_date = end_date - datetime.timedelta(days=90)

    try:
        transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")
        logger.info("Формат даты в файле успешно обработан.")
    except ValueError as e:
        logger.error(f"Не удалось определить формат даты в столбце: {e}.")
        raise ValueError("Не удалось определить формат даты в столбце.") from e

    filtered_transactions = transactions[
        (transactions["Дата платежа"] >= start_date)
        & (transactions["Дата платежа"] <= end_date)
        & (transactions["Категория"] == category)
    ].copy()

    filtered_transactions["Дата платежа"] = filtered_transactions["Дата платежа"].dt.strftime("%d.%m.%Y")
    logger.info("Данные успешно отфильтрованы.")

    result = filtered_transactions.to_json(orient="records", force_ascii=False)

    return result
