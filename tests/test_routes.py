import pytest
import io
from flask import get_flashed_messages


def test_upload_file(client):
    """Отправка GET запроса на главную страницу.
    Проверяем наличие кнопки с текстом 'Выберите CSV файл'."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert 'Выберите CSV файл' in rv.data.decode('utf-8')


def test_upload_invalid_file(client):
    """Отправка POST запроса с файлом не формата csv."""
    formats = ('.xlsx', '.txt', '.docx', '.pdf', '.doc', '.pptx', '.jpg', '.png', '.jpeg', '.gif', 'xls')
    for f in formats:
        file_test = io.BytesIO(b'test')
        rv = client.post('/upload', data={'file': (file_test, f"test{f}")}, follow_redirects=True)
        assert "Неверный формат файла" in rv.data.decode('utf-8')


def test_upload_invalid_date(client):
    """Отправка POST запроса с файлом формата csv, содержащим некорректный формат дат."""
    invalid_date_rows = ("2025-01-03Продукты,1500", "01.01.2025,Продукты,1500")
    #TODO: Убрать сообщение о неверном формате даты
    for row in invalid_date_rows:
        file_context = f"date,category,amount\n{row}".encode('utf-8')
        file_test = io.BytesIO(file_context)
        rv = client.post('/upload', data={'file': (file_test, 'test.csv')}, follow_redirects=True)
        print(get_flashed_messages())
        assert "Неверный формат даты" in rv.data.decode('utf-8')
