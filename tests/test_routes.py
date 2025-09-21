import pytest
import io
from flask import get_flashed_messages


def create_io_file(context: str) -> io.BytesIO:
    """Подготовка файла для отправки на сервер."""
    if isinstance(context, str):
        file_context = context.encode('utf-8')
        return io.BytesIO(file_context)

    return io.BytesIO(b'')


def test_upload_file(client):
    """Отправка GET запроса на главную страницу.
    Проверяем наличие кнопки с текстом 'Выберите CSV файл'."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Выберите CSV файл' in response.data.decode('utf-8')


def test_upload_invalid_file(client):
    """Отправка POST запроса с файлом не формата csv."""
    formats = ('.xlsx', '.txt', '.docx', '.pdf', '.doc', '.pptx', '.jpg', '.png', '.jpeg', '.gif', 'xls')
    for f in formats:
        file_test = io.BytesIO(b'test')
        response = client.post('/upload', data={'file': (file_test, f"test{f}")}, follow_redirects=True)
        assert "Неверный формат файла" in response.data.decode('utf-8')


def test_upload_invalid_date(client):
    """Отправка POST запроса с файлом формата csv, содержащим некорректный формат дат."""
    invalid_date_rows = ("2025-01-03Продукты,1500", "01 март 2024,Продукты,1500",)
    for row in invalid_date_rows:
        file_test = create_io_file("date,category,amount\n" + row)
        response = client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
        assert "Неверный формат даты" in response.data.decode('utf-8')


def test_upload_valid_file(client):
    """Отправка POST запроса с файлом с корректными данными."""
    valid_rows = "date,category,amount\n01.03.2024,Продукты,1500\n2025-01-05,Фитнес,2500\n2025-01-06,Путешествия,12000"
    file_test = create_io_file(valid_rows)
    client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
    assert "Файл успешно загружен!" in get_flashed_messages()


def test_upload_empty_file(client):
    """Отправка POST запроса с пустым файлом."""
    file_test = io.BytesIO(b'')
    client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
    assert "Файл пустой." in get_flashed_messages()

    file_test = create_io_file("date,category,amount\n")
    response = client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
    assert "Файл пуст" in response.data.decode('utf-8')


def test_upload_invalid_amount_format(client):
    """Отправка POST запроса с файлом с некорректным форматом суммы."""
    file_test = create_io_file("date,category,amount\n2025-01-01,Продукты,стоимость")
    response = client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
    assert "неверный формат суммы" in response.data.decode('utf-8')


def test_csv_read_error(client):
    """Тест на обработку ошибки при чтении CSV"""
    file_test = create_io_file("дата,категория,сумма\n2025-01-01,Продукты,1500")  # некорректная кодировка
    response = client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
    assert "Ошибка в файле" in response.data.decode('utf-8')


def test_missing_columns_in_csv(client):
    """Тест на отсутствие необходимых столбцов в CSV"""
    file_test = create_io_file("date,amount\n2025-01-01,1500")
    response = client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
    assert "Отсутствуют столбцы: category" in response.data.decode('utf-8')
