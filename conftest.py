import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture()
def browser():
    # 1. SETUP: Скачиваем ChromeDriver и запускаем браузер Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)
    
    # 2. Передаем управление и объект драйвера в тест
    yield driver
    
    # 3. TEARDOWN: Гарантированно закрываем браузер после окончания теста
    print("\nЗакрываем браузер...")
    driver.quit()
