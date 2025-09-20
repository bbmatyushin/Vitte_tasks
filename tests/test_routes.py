import pytest


def test_upload_file(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert 'Выберите CSV файл' in rv.data.decode('utf-8')