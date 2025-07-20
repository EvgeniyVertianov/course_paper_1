from datetime import datetime
import os
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
import requests

from src.utils import greet


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