from flask import Flask
from config import Config
import time


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # информация пользователю о запуске приложения
    app.config["APP_START_TIME"] = time.time()

    from app.routes import main_bp  # регистрация blueprint
    app.register_blueprint(main_bp)

    return app
