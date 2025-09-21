import pandas as pd
from pandas import DataFrame
from typing import Tuple
from flask import request, session


class ValidatorCSV:
    ALLOWED_EXTENSIONS = ('csv',)
    CSV_HEADERS = ("date", "category", "amount",)

    @classmethod
    def allowed_file(cls, filename: str) -> bool:
        """Проверка на разрешенные типы файлов"""
        result = '.' in filename and \
                 filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS
        return result

    @classmethod
    def csv_columns_validate(cls, df: DataFrame) -> Tuple[bool, str]:
        """Проверка корректно указанных названий столбцов в CSV файле"""
        missing_columns = [column for column in cls.CSV_HEADERS if column not in df.columns]

        if missing_columns:
            return False, f"Отсутствуют столбцы: {', '.join(missing_columns)}"

        if df.empty:
            return False, "Файл пуст"

        # Проверка формата даты в поле date
        try:
            df["date"] = pd.to_datetime(df["date"], errors='raise')
        except ValueError:
            return False, "Неверный формат даты. Формат даты должен быть: YYYY-MM-DD или DD.MM.YYYY"

        # Проверка формата суммы в поле amount
        try:
            df["amount"] = df["amount"].astype(float)
        except ValueError:
            return False, "У одной из записи неверный формат суммы. Формат суммы должен быть: числом"

        return True, "Ok"
