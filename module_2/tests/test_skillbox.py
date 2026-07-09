import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="function")
def driver():
    """
    Фикстура для инициализации и закрытия локального браузера Chrome.
    Использует webdriver-manager для автоматического подбора ChromeDriver.
    """
    # Настраиваем автоматическую установку правильной версии ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    # Инициализируем локальный браузер
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    yield driver
    
    # Гарантированно закрываем браузер после теста
    driver.quit()


def test_skillbox_title(driver):
    """
    Тест-кейс: Проверка title главной страницы Skillbox
    """
    # Шаг 1: Открываем тестируемый сайт
    driver.get("https://skillbox.ru/")
    
    # Шаг 2: Получаем текущий заголовок вкладки браузера
    actual_title = driver.title
    
    # Ожидаемый заголовок (или его часть)
    expected_part = "Skillbox"
    
    # Шаг 3: Проверка (Assertion)
    assert expected_part in actual_title, f"Ожидалось, что '{expected_part}' содержится в заголовке '{actual_title}'"