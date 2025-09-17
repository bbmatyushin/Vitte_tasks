import os


class Config:
    DEBUG = True
    SECRET_KEY = '123456'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # создание папки для загрузки файлов


