import time
from functools import wraps
from typing import Optional
from flask import session


class Cache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # паттерн Singleton
        if not cls._instance:
            cls._instance = super(Cache, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'cache'):  # чтобы не перезаписывать при повторном вызове
            self.cache = {}
            self.ttl = 300

    def set_ttl(self, ttl):
        """Установить время жизни кеша в секундах"""
        self.ttl = ttl

    def get_key(self, filename: str, user: str) -> str:
        """Сформировать ключ по имени файла и имени пользователя.
        Пользователь гипотетический. Если реализовать регистрация в приложении,
        то можно получит имя зарегистрированного пользователя."""
        return f"{filename}_{user}"

    def is_expired(self, timestamp: float) -> bool:
        """Проверить, истекло ли время действия кеша"""
        return time.time() - timestamp > self.ttl

    def get(self, filename: str, user: str) -> Optional[str]:
        """Вернуть значение из кеша или None, если кеша нет или просрочен"""
        key = self.get_key(filename, user)
        if key not in self.cache:
            return None
        cached_time, result = self.cache[key]
        if self.is_expired(cached_time):
            self.cache.pop(key)
            return None
        return result

    def set(self, filename: str, user: str, result: str) -> None:
        """Сохранить результат в кеш"""
        cache_key = self.get_key(filename, user)
        self.cache[cache_key] = (time.time(), result)

    def clear(self):
        """Очистить весь кеш."""
        size = len(self.cache)
        self.cache.clear()
        return size

    def stats(self):
        """Статистика: размер кеша и ключи."""
        return {
            "size": len(self.cache),
            "keys": list(self.cache.keys())
        }

    # декоратор для кеширования
    def cached(self, ttl: int = 300):
        """Декоратор для кеширования функции"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # генерируем ключ из имени файла и действия
                filename = session.get('filename')
                user = "superuser"

                if not filename or not user:
                    return func(*args, **kwargs)

                self.set_ttl(ttl)
                cached_result = self.get(filename, user)
                if cached_result is not None:
                    return cached_result

                result = func(*args, **kwargs)
                self.set(filename, user, result)
                return result
            return wrapper
        return decorator
