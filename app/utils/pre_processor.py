import pandas as pd
from pandas import DataFrame, Series
from typing import Optional, Tuple, Union
from .cache import Cache


cache = Cache()


class PreProcessor:
    @classmethod
    @cache.cached()  # Декоратор для кеширования результатов
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
