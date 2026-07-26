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

def test_github_advanced_search():
    """Кейс №3: Расширенный поиск GitHub с выпадающими списками"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/search/advanced')

    wait = WebDriverWait(driver, 10)

    # 1. Кликаем на поле языка, чтобы открыть дропдаун
    language_field = wait.until(
        EC.element_to_be_clickable((By.ID, "search_language"))
    )
    language_field.click()
    
    # 2. Выбираем Python из дропдауна (скроллим если нужно)
    python_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//option[@value='Python']"))
    )
    python_option.click()

    # 3. Вводим количество звёзд >20000
    stars_input = wait.until(
        EC.presence_of_element_located((By.ID, "search_stars"))
    )
    stars_input.send_keys(">20000")

    # 4. Вводим имя файла environment.yml
    filename_input = wait.until(
        EC.presence_of_element_located((By.ID, "search_filename"))
    )
    filename_input.send_keys("environment.yml")

    # 5. Нажимаем кнопку поиска
    search_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
    )
    search_button.click()

    # 6. Пауза 5 секунд для визуальной проверки
    time.sleep(5)
    driver.quit()

def test_github_commit_activity_hover():
    """Кейс №5: Проверка наведения мыши на график активности коммитов"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/graphs/commit-activity')

    wait = WebDriverWait(driver, 10)

    # 1. Находим один из столбцов графика Highcharts
    chart_bar = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".highcharts-point"))
    )

    # 2. Выполняем наведение мыши на столбец через ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(chart_bar).perform()

    # 3. Ждем появления всплывающей подсказки (указываем точный SVG-тег g)
    tooltip = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "g.highcharts-tooltip"))
    )

    # 4. Проверяем, что подсказка отобразилась
    assert tooltip.is_displayed(), "Tooltip не отображается при наведении!"

    time.sleep(3)
    driver.quit()

def test_skillbox_course_filters():
    """Кейс №4: Фильтрация курсов на Skillbox (Профессия, 6-12 месяцев, Docker)"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://skillbox.ru/code/')

    wait = WebDriverWait(driver, 10)

    # 1. Открываем окно фильтров
    filter_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Фильтры')]"))
    )
    filter_btn.click()

    # 2. Выбираем вкладку "Профессия" через JS (обход всплывающей подсказки)
    profession_tab = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, 
            "//button[contains(@class, 'programs-filter-group__tab') and contains(., 'Профессия')]"
        ))
    )
    driver.execute_script("arguments[0].click();", profession_tab)
    time.sleep(1)

    # 3. Выбираем диапазон длительности "От 6 до 12 мес."
    duration_tab = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, 
            "//button[contains(@class, 'programs-filter-group__tab') and contains(., 'От 6 до 12 мес.')]"
        ))
    )
    driver.execute_script("arguments[0].click();", duration_tab)
    time.sleep(1)

    # 4. Выбираем тематику "Docker"
    topic_tab = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, 
            "//button[contains(@class, 'programs-filter-group__tab') and contains(., 'Docker')]"
        ))
    )
    driver.execute_script("arguments[0].click();", topic_tab)
    time.sleep(1)

    # 5. Нажимаем кнопку "Применить"
    apply_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Применить')]"))
    )
    driver.execute_script("arguments[0].click();", apply_button)

    # 6. Проверка результатов: ждем обновления карточек курсов
    time.sleep(3)
    cards = wait.until(
        EC.presence_of_all_elements_located((
            By.XPATH, 
            "//article[contains(@class, 'product-card')] | //div[contains(@class, 'product-card')]"
        ))
    )
    
    assert len(cards) > 0, "После применения фильтров карточки курсов не найдены!"

    time.sleep(3)
    driver.quit()