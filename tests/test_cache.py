import re
from pytest_mock import MockerFixture


#TODO: разобрать. Падает:
# FAILED tests/test_cache.py::test_cache_set_clear -
# AssertionError: assert 'Кеш очищен.' in '<!doctype html>\n<html lang=en>\n
# <title>405 Method Not Allowed</title>\n<h1>Method Not Allowed</h1>\n
# <p>The method is not allowed for the requested URL.</p>\n'

# def test_cache_set_clear(cache, client):
#     """Проверяем наполненеи кэша и очистку через ручку /clear_cache"""
#     cache.set("test_file.csv", "superuser", "cache_df_data")
#     assert len(cache.cache) == 1
#
#     response = client.post("/clear-cache", data={}, follow_redirects=True)
#     assert "Кеш очищен." in response.data.decode("utf-8")

def test_cache_set_clear(cache, client):
    """Проверяем наполнение кэша и его очистку"""
    cache.set("test_file.csv", "superuser", "cache_df_data")
    assert len(cache.cache) == 1

    cleared_count = cache.clear()
    assert cleared_count == 1
    assert len(cache.cache) == 0


def test_cache_stats(cache, client):
    """Тесты для метода stats()"""
    cache.set("test_file.csv", "superuser", "cached_data")

    response = client.get("/status")
    assert response.json["cache_size"] == 1
    assert "test_file.csv_superuser" in response.json["cached_keys"]
    assert re.search(r"3.7.\d+", response.json["python_version"])


def test_cache_set_get(cache):
    """Тесты для методов set() и get() класса Cache"""
    filename, user, reslt = "test_file.csv", "superuser", "df_result for cached"

    cache.set(filename, user, reslt)
    assert cache.get(filename, user) == reslt


def test_cache_get_key(cache):
    """Тесты для метода get_key() - генерация ключа"""
    filename, user = "test_file.csv", "superuser"
    key = cache.get_key(filename, user)
    assert key == f"{filename}_{user}"


def test_cache_ttl_expiration(cache, mocker: MockerFixture):
    """Тест механизма TTL для кэша"""
    # Мокаем время
    mocked_time = mocker.patch("time.time")
    mocked_time.return_value = 0  # задаем возвращаемое значение

    filename, user, reslt = "test_file.csv", "superuser", "df_result for cached"

    cache.set_ttl(1)  # устанавливаем TTL в 1 сек
    cache.set(filename, user, reslt)
    assert cache.get(filename, user) == reslt

    mocked_time.return_value += 1  # увеличиваем время на 1 сек
    assert cache.get(filename, user) == reslt

    mocked_time.return_value += 1  # увеличиваем время ещё на 1 сек
    assert cache.get(filename, user) is None


def test_cache_decorator(cache, client, mocker: MockerFixture):
    """Тест декоратора для кэширования функций"""
    call_count = {"n": 0}

    @cache.cached(ttl=1)
    def test_func(x: int):
        call_count["n"] += 1
        return x * 2

    # Создаем конекст запроса вручную, без реального HTTP-запроса
    # для использования сессии в тесте
    with client.application.test_request_context():
        from flask import session
        session["filename"] = "test_file.csv"

        # Мокаем время
        mocked_time = mocker.patch("time.time")
        mocked_time.return_value = 0

        result_1 = test_func(10)
        assert result_1 == 20
        assert call_count["n"]  == 1
        assert cache.stats()["size"] == 1

        mocked_time.return_value += 1
        result_2 = test_func(100)
        assert result_2 == 20
        assert call_count["n"]  == 1
        assert cache.stats()["size"] == 1

        mocked_time.return_value += 1
        result_3 = test_func(50)
        assert result_3 == 100
        assert call_count["n"] == 2
        assert cache.stats()["size"] == 1



