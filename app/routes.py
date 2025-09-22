import json
import os
import pandas as pd
import platform
import time
from datetime import datetime
from pathlib import Path
from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, current_app, session,
    jsonify
)

from .utils.validator_csv import ValidatorCSV
from .utils.pre_processor import PreProcessor, cache


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    return render_template("uploads.html")


@main_bp.route("/upload", methods=["POST"])
def upload_file():
    """Страница загрузки файла"""
    if request.method == "POST":

        if "file" not in request.files:  # Проверка на наличие файла
            flash("Файл не выбран", "error")
        else:
            file = request.files["file"]
            file_path = Path(current_app.config["UPLOAD_FOLDER"], file.filename)
            file.save(Path(file_path))  # Сохранение файла в папку uploads
            session["filename"] = file.filename

            if not file_path.exists():  # Проверка на существование файла
                flash("Файл не был успешно загружен", "error")
            elif os.path.getsize(file_path) == 0:
                flash("Файл пустой.", "error")
            elif file and ValidatorCSV.allowed_file(file.filename):
                try:
                    current_app.logger.info(f"Файл {file.filename} загружен")

                    df = pd.read_csv(file_path, encoding="utf-8")
                    is_valid, message = ValidatorCSV.csv_columns_validate(df)
                    if not is_valid:
                        flash(f"Ошибка в файле: {message}", "error")
                    else:
                        flash("Файл успешно загружен!", "success")
                        return redirect(url_for("main.analyze"))
                except Exception as e:
                    flash(f"Ошибка обработке файла: {e}", "error")
                    current_app.logger.error(f"Ошибка обработке файла: {e}", "error")
            else:
                flash("Неверный формат файла. Загрузите файл фомарта csv", "error")

    return redirect(url_for("main.index"))


@main_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Страница анализа расходов"""
    # Проверка наличия пути к файлу в сессии
    file_path: Path = \
        Path(current_app.config["UPLOAD_FOLDER"], session["filename"]) if "filename" in session else None

    if file_path is None or not file_path.exists():
        flash("Сначала необходимо загрузить CSV файл", "error")
        return redirect(url_for("main.upload_file"))

    df = pd.read_csv(str(file_path), encoding="utf-8")
    df = PreProcessor.process_df(df)  # обработка и сортировка данных для анализа

    analysis_result = analysis_type = column_name = None
    months, years = PreProcessor.get_months_years(df)

    if request.method == "POST":
        action = request.form.get("action")
        category_checked = request.form.get("analysis_type")
        if category_checked:
            session["category_checked"] = request.form.get("analysis_type")  # Сохранение выбранной радиокнопки

        if action == "category_analysis":
            selected_years = request.form.getlist("selected_years")  # Получение выбранных годов
            selected_months = request.form.getlist("selected_months")  # Получение выбранных месяцев

            # Преобразование строки в список
            selected_months = json.loads(selected_months[0])
            selected_years = json.loads(selected_years[0])
            if selected_years:
                selected_years = list(map(int, selected_years))  # Преобразование в список чисел

            current_app.logger.debug(f"selected_years={selected_years}, selected_months={selected_months}")

            if session["category_checked"] == 'period':
                # Анализ по датам для категорий
                if selected_years and selected_months:
                    analysis_result, analysis_type, column_name = \
                        PreProcessor.dates_analysis(df, "month_year", selected_years, selected_months)
                elif selected_years:
                    analysis_result, analysis_type, column_name = \
                        PreProcessor.dates_analysis(df, "year", selected_years=selected_years)
                elif selected_months:
                    analysis_result, analysis_type, column_name = \
                        PreProcessor.dates_analysis(df, "month", selected_months=selected_months)
                else:
                    flash("Не выбран период для анализа", "error")
            else:
                # Анализ по категориям
                analysis_result, analysis_type, column_name = PreProcessor.category_analysis(df)

        elif action == "time_analysis":
            # Анализ по дням / месяцам / годам (выбор периода в форме)
            period = request.form.get("period", "month")

            if period == "day":
                df["period"] = df["date"].dt.strftime("%Y-%m-%d")
                period_name = "Анализ по дням"
            elif period == "month":
                df["period"] = df["date"].dt.strftime("%Y-%m")
                period_name = "Анализ по месяцам"
            elif period == "year":
                df["period"] = df["date"].dt.strftime("%Y")
                period_name = "Анализ по годам"
            else:
                flash("Неизвестный период для анализа", "error")
                return render_template("analyze.html")

            time_sums = df.groupby("period")["amount"].sum().sort_index()  # сортировка по индексу (периоду)

            analysis_result = {
                "type": "time",
                "data": time_sums.to_dict(),
                "period": period,
                "total": df["amount"].sum(),
            }
            analysis_type = period_name
            column_name = "Период"

    current_app.logger.debug(f"analysis_result={analysis_result}")

    return render_template(
        "analyze.html",
        analysis_result=analysis_result,
        analysis_type=analysis_type,
        months_name=months,
        years=years,
        category_checked=session.get("category_checked", "category"),
        column_name=column_name
    )


@main_bp.route("/clear-cache", methods=["POST"])
def clear_cache():
    """Очищаем весь кэш"""
    cleared = cache.clear()
    flash(f"Кеш очищен. Удалено элементов: {cleared}", "success")
    return redirect(request.referrer or url_for("main.analyze"))


@main_bp.route("/status", methods=["GET"])
def status():
    stats = cache.stats()
    start_time = datetime.fromtimestamp(current_app.config["APP_START_TIME"]).strftime('%Y-%m-%d %H:%M:%S')
    uptime = time.time() - current_app.config["APP_START_TIME"]

    return jsonify({
        "uptime_seconds": f"{uptime:.3f} sec.",
        "cache_size": stats["size"],
        "cached_keys": stats["keys"],
        "app_start_time": start_time,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    })

