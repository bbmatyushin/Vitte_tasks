from typing import Optional
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


class PreProcessor:
    @classmethod
    def process_df(cls, df: DataFrame) -> DataFrame:
        """Обработка и отчистка данных в DataFrame. Используется после
        выполнения проверок методами csv_columns_validate и allowed_file"""

        month_names = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }

        # Преобразовываем типы данных
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["month_name"] = df["month"].map(month_names)
        df["year_month"] = df["year"].astype(str) + " | " + df["month_name"]

        # Убираем лишние пробелы
        df["category"] = df["category"].str.strip()

        df = df.sort_values("date")

        return df

    @classmethod
    def get_months_years(cls, df: DataFrame) -> tuple:
        """Получение списка месяцев и годов из DataFrame"""
        years = sorted(df["year"].unique())
        months = df.sort_values(["month"])["month_name"].unique()

        return months, years

    @classmethod
    def category_analysis(cls, df: DataFrame) -> tuple:
        """Обработка данных по категориям"""
        category_sums = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        total_amount = df["amount"].sum()

        analysis_result = {
            "type": "category",
            "data": category_sums.to_dict(),
            "total": total_amount,
            "column_name": "Категория"
        }
        analysis_type = "Анализ по категориям"
        column_name = "Категория"

        return analysis_result, analysis_type, column_name

    @classmethod
    def dates_analysis(cls, df: DataFrame, date_type: Optional[str],
                       selected_years: list = list,
                       selected_months: list = list) -> tuple:
        """Обработка данных по датам

        :param df: DataFrame с данными
        :param date_type: тип даты (month, year, month_year)
        :param selected_years: список выбранных годов
        :param selected_months: список выбранных месяцев
        """

        if date_type == 'year':
            df = df[df["year"].isin(selected_years)]
            dates_sums = df.groupby(df["year"])["amount"].sum().sort_values(ascending=False)
        elif date_type == 'month':
            df = df[df["month_name"].isin(selected_months)]
            dates_sums = df.groupby(df["month_name"])["amount"].sum().sort_values(ascending=False)
        else:
            df = df[(df["year"].isin(selected_years)) & (df["month_name"].isin(selected_months))]
            dates_sums = df.groupby(df["year_month"])["amount"] \
                .sum() \
                .sort_values(ascending=False)

        total_amount = df["amount"].sum()

        analysis_result = {
            "type": date_type,
            "data": dates_sums.to_dict(),
            "total": total_amount,
        }
        analysis_type = "Анализ по категориям"
        column_name = "Период"

        return analysis_result, analysis_type, column_name


