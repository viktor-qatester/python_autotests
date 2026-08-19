"""Подключаем фикстуры из src/fixtures — pytest сам эту папку не обходит."""

pytest_plugins = ["src.fixtures.browser"]
