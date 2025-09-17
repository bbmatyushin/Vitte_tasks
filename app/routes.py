import pandas as pd
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from .utils import ValidatorCSV, process_df


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def upload_file():
    """Страница загрузки файла"""
    if request.method == "POST":

        if "file" not in request.files:  # Проверка на наличие файла
            flash("Файл не выбран", "error")
            return redirect(request.url)

        file = request.files["file"]
        file_path = Path(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(Path(file_path))  # Сохранение файла в папку uploads

        current_app.config["csv_file_path"] = file_path

        if file and ValidatorCSV.allowed_file(file.filename):
            try:
                if not file_path.exists():  # Проверка на существование файла
                    flash("Файл не был успешно загружен", "error")
                    return redirect(request.url)

                current_app.logger.info(f"Файл {file.filename} загружен")

                df = pd.read_csv(file_path, encoding="utf-8")
                is_valid, message = ValidatorCSV.csv_columns_validate(df)
                if not is_valid:
                    flash(f"Ошибка в файле: {message}", "error")
                    return render_template("uploads.html")

                flash("Файл успешно загружен!", "success")
                return redirect(url_for("main.analyze"))

            except Exception as e:
                current_app.logger.error(f"Ошибка обработки файла: {e}", "error")
                return render_template("uploads.html")

    return render_template("uploads.html")


@main_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Страница анализа расходов"""
    # Проверка наличия пути к файлу в сессии
    file_path: Path = current_app.config.get("csv_file_path")

    if not file_path or not file_path.exists():
        flash("Сначала необходимо загрузить CSV файл", "error")
        return redirect(url_for("main_bp.upload_file"))

    df = pd.read_csv(str(file_path), encoding="utf-8")
    df = process_df(df)  # обработка и сортировка данных для анализа

    analysis_result = analysis_type = None

    if request.method == "POST":
        action = request.form.get("action")

        #TODO: сделать отдельные методы для каждого типа анализа
        if action == "category_analysis":
            # Анализ по категориям
            category_sums = df.groupby("category")["amount"].sum().sort_values(ascending=False)
            total_amount = df["amount"].sum()

            analysis_result = {
                "type": "category",
                "data": category_sums.to_dict(),
                "total": total_amount,
            }
            analysis_type = "Анализ по категориям"

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

    return render_template(
        "analyze.html",
        analysis_result=analysis_result,
        analysis_type=analysis_type,
    )


@main_bp.errorhandler(404)
def handle_error(error):
    flash(f"Страница не найдена", "error")
    return redirect(url_for("main_bp.upload_file"))
