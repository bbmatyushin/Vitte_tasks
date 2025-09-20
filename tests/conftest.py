import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

import pytest
from app import create_app
import tempfile


@pytest.fixture
def client():
    """Создание тестового приложения Flask"""
    app = create_app()
    app.config['TESTING'] = True
    app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()

    with app.test_client() as client:
        yield client
        os.rmdir(app.config["UPLOAD_FOLDER"])
