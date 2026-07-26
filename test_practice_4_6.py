import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def test_github_issues_search():
    # 1. Запуск браузера и переход на страницу
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/issues')

    wait = WebDriverWait(driver, 10)

    # 2. Находим кнопку поиска (универсальный XPath для десктопной и мобильной версий)
    search_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, 
            "//button[contains(@class, 'Search') or contains(@class, 'search') or contains(@data-component, 'Search')]"
        ))
    )
    search_button.click()

    # 3. Находим появившееся поле ввода query-builder-test
    search_input = wait.until(
        EC.element_to_be_clickable((By.ID, "query-builder-test"))
    )

    # 4. Вводим фильтр и ключевое слово bug, затем нажимаем Enter
    search_input.send_keys("in:title bug", Keys.ENTER)

    # 5. Пауза 5 секунд для визуальной проверки
    time.sleep(5)
    driver.quit()

def test_github_author_filter():
    """Кейс №2: Фильтрация по автору через выпадающее меню Author"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/issues')

    wait = WebDriverWait(driver, 10)

    # 1. Открываем выпадающее меню Author
    author_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'authorFilterButton')]"))
    )
    author_button.click()

    # 2. Вводим имя автора bpasero в поле поиска авторов
    author_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Filter authors']"))
    )
    author_input.send_keys("bpasero")

    # 3. Выбираем найденного автора из списка по точному тексту
    author_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='author:bpasero']"))
    )
    author_option.click()

    # 4. Пауза 5 секунд для визуальной проверки
    time.sleep(5)
    driver.quit()