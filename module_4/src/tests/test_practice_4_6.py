import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


def test_github_issues_search():
    """Кейс №1: Поиск в Issues по ключевому слову"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/issues')

    wait = WebDriverWait(driver, 10)

    # 1. Находим и открываем поле поиска
    search_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, 
            "//button[contains(@class, 'Search') or contains(@class, 'search') or contains(@data-component, 'Search')]"
        ))
    )
    search_button.click()

    # 2. Находим поле ввода
    search_input = wait.until(
        EC.element_to_be_clickable((By.ID, "query-builder-test"))
    )

    # 3. Вводим поисковый запрос
    search_input.send_keys("in:title bug", Keys.ENTER)
    time.sleep(2)

    # 4. ASSERT: Проверяем, что поиск применился (текст появился в поисковой строке или URL)
    current_url = driver.current_url
    assert "bug" in current_url or "bug" in search_input.get_attribute("value"), "Фильтр bug не применился в поиске!"

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

    # 3. Выбираем найденого автора из списка по точному тексту
    author_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='author:bpasero']"))
    )
    author_option.click()
    time.sleep(2)

    # 4. ASSERT: Проверяем, что автор подставился в URL или в строку поиска
    current_url = driver.current_url
    assert "bpasero" in current_url, "Фильтр по автору bpasero не отображается в URL!"

    driver.quit()


def test_github_advanced_search():
    """Кейс №3: Расширенный поиск GitHub с выпадающими списками"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/search/advanced')

    wait = WebDriverWait(driver, 10)

    # 1. Выбираем язык Python
    language_field = wait.until(
        EC.element_to_be_clickable((By.ID, "search_language"))
    )
    language_field.click()
    
    python_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//option[@value='Python']"))
    )
    python_option.click()

    # 2. Вводим количество звёзд >20000
    stars_input = wait.until(
        EC.presence_of_element_located((By.ID, "search_stars"))
    )
    stars_input.send_keys(">20000")

    # 3. Вводим имя файла environment.yml
    filename_input = wait.until(
        EC.presence_of_element_located((By.ID, "search_filename"))
    )
    filename_input.send_keys("environment.yml")

    # 4. Нажимаем кнопку поиска
    search_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
    )
    search_button.click()
    time.sleep(3)

    # 5. ASSERT: Проверяем, что в URL появились параметры поиска Python
    assert "Python" in driver.current_url or "language%3APython" in driver.current_url or "l=Python" in driver.current_url, "Параметры поиска Python не найдены в URL!"

    driver.quit()


def test_skillbox_course_filters():
    """Кейс №4: Фильтрация курсов на Skillbox"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://skillbox.ru/code/')

    wait = WebDriverWait(driver, 10)

    # Закрываем куки-банер, если он появляется
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(., 'Согласен') or contains(., 'Принять')]")
        cookie_btn.click()
    except Exception:
        pass

    # 1. Открываем окно фильтров
    filter_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Фильтры')]"))
    )
    driver.execute_script("arguments[0].click();", filter_btn)
    time.sleep(1)

    # 2. Выбираем "Профессия"
    try:
        profession_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Профессия')] | //label[contains(., 'Профессия')]"))
        )
        driver.execute_script("arguments[0].click();", profession_tab)
    except Exception:
        pass

    # 3. Нажимаем "Применить"
    apply_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Применить') or contains(., 'Показать')]"))
    )
    driver.execute_script("arguments[0].click();", apply_button)

    # 4. ASSERT: Ждем загрузки результатов и проверяем наличие карточек
    time.sleep(3)
    cards = wait.until(
        EC.presence_of_all_elements_located((
            By.XPATH, 
            "//article | //a[contains(@class, 'card')] | //div[contains(@class, 'card')]"
        ))
    )
    
    assert len(cards) > 0, "После применения фильтров карточки курсов не найдены!"

    driver.quit()


def test_github_commit_activity_hover():
    """Кейс №5: Проверка наведения мыши на график активности коммитов"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/graphs/commit-activity')

    wait = WebDriverWait(driver, 10)

    # 1. Находим столбец графика
    chart_bar = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".highcharts-point"))
    )

    # 2. Наведение мыши
    actions = ActionChains(driver)
    actions.move_to_element(chart_bar).perform()

    # 3. Подсказка
    tooltip = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "g.highcharts-tooltip"))
    )

    # 4. ASSERT: Проверяем видимость подсказки
    assert tooltip.is_displayed(), "Tooltip не отображается при наведении!"

    driver.quit()