import os
import pytest
from app import create_app
import tempfile
from app.utils.cache import Cache


@pytest.fixture
def client():
    """Создание тестового приложения Flask"""
    app = create_app()
    app.config['TESTING'] = True
    app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()

    with app.test_client() as client:
        yield client

    # Удаление файлов после завершения теста
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


@pytest.fixture
def cache():
    return Cache()

