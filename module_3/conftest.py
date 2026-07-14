import pytest
from selenium import webdriver

@pytest.fixture()
def set_up_browser():
    # Инициализируем локальный Chrome
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)  # Неявное ожидание элементов (чтобы тест не падал сразу, если сайт тормозит)
    driver.maximize_window()     # Разворачиваем браузер на весь экран
    
    yield driver  # Передаем управление в тест-кейс
    
    driver.quit()  # После окончания теста закрываем браузер