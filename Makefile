.PHONY: test clean

# Команда по умолчанию для запуска всех тестов из папки tests
test:
	pytest

# Команда для очистки проекта от временных файлов кэша Python и pytest
clean:
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache, **/___pycache___
