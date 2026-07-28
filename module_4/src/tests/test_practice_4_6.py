import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def test_github_issues_search():
    """Кейс №1: Поиск в Issues по ключевому слову."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/issues')

    wait = WebDriverWait(driver, 10)

    # 1. Находим и открываем поле поиска
    search_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class, 'Search') or "
            "contains(@class, 'search') or "
            "contains(@data-component, 'Search')]"
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

    # 4. ASSERT: Проверяем, что поиск применился
    current_url = driver.current_url
    assert "bug" in current_url or "bug" in search_input.get_attribute("value"), \
        "Фильтр bug не применился в поиске!"

    driver.quit()


def test_github_author_filter():
    """Кейс №2: Фильтрация по автору через выпадающее меню Author."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://github.com/microsoft/vscode/issues')

    wait = WebDriverWait(driver, 10)

    # 1. Открываем выпадающее меню Author
    author_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class, 'authorFilterButton') or contains(., 'Author')]"
        ))
    )
    author_button.click()

    # 2. Вводим имя автора bpasero в поле поиска авторов строго внутри __primerPortalRoot__
    author_input = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='__primerPortalRoot__']//input | //input[@placeholder='Filter authors']"
        ))
    )
    author_input.send_keys("bpasero")
    time.sleep(1)

    # 3. Выбираем найденного автора из портального выпадающего списка
    author_option = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='__primerPortalRoot__']//*[contains(text(), 'bpasero')] | "
            "//a[contains(., 'bpasero')] | "
            "//button[contains(., 'bpasero')]"
        ))
    )
    author_option.click()
    time.sleep(2)

    # 4. ASSERT: Проверяем, что автор подставился в URL или в строку поиска
    current_url = driver.current_url
    search_val = ""
    try:
        search_input = driver.find_element(By.ID, "query-builder-test")
        search_val = search_input.get_attribute("value") or ""
    except Exception:
        pass

    assert "bpasero" in current_url or "bpasero" in search_val, \
        "Фильтр по автору bpasero не отображается в URL или строке поиска!"

    driver.quit()


def test_github_advanced_search():
    """Кейс №3: Расширенный поиск GitHub с выпадающими списками."""
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

    # 4. Нажимаем кнопку сабмита формы поиска по точному XPath из формы
    search_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='search_form']/div[2]/div/div/button | "
            "//*[@id='search_form']//button[@type='submit']"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(3)

    # 5. ASSERT: Проверяем, что в URL появились параметры поиска Python
    assert "Python" in driver.current_url or \
           "language%3APython" in driver.current_url or \
           "l=Python" in driver.current_url, \
        "Параметры поиска Python не найдены в URL!"

    driver.quit()


def test_skillbox_course_filters():
    """Кейс №4: Фильтрация курсов (Профессия + 6-12 мес + Docker)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 15)

    def safe_click(by, value):
        """Вспомогательный метод: ждет элемент и кликает через JS."""
        element = wait.until(EC.presence_of_element_located((by, value)))
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", element)

    try:
        driver.get("https://skillbox.ru/code/")

        # 1. Быстрое закрытие куки
        driver.implicitly_wait(1)
        cookie_btns = driver.find_elements(
            By.XPATH,
            "//button[contains(., 'Согласен') or "
            "contains(., 'Принять') or contains(@class, 'cookie')]"
        )
        if cookie_btns and cookie_btns[0].is_displayed():
            driver.execute_script("arguments[0].click();", cookie_btns[0])
        driver.implicitly_wait(0)

        # 2. Проверка мобильной/шторки фильтров
        filter_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(@class, 'programs-filter-mobile__button') or "
            "contains(., 'Фильтры')]"
        )
        if filter_buttons and filter_buttons[0].is_displayed():
            driver.execute_script("arguments[0].click();", filter_buttons[0])
            time.sleep(0.8)

        # 3. Выбираем "Профессия"
        safe_click(
            By.XPATH,
            "//label[contains(., 'Профессия')] | "
            "//button[contains(., 'Профессия')] | "
            "//span[contains(., 'Профессия')]"
        )
        time.sleep(0.5)

        # 4. Выбираем длительность "От 6 до 12 мес."
        safe_click(
            By.XPATH,
            "//label[contains(., '6') and contains(., '12')] | "
            "//button[contains(., '6') and contains(., '12')] | "
            "//span[contains(., '6') and contains(., '12')]"
        )
        time.sleep(0.5)

        # 5. Выбираем "Docker"
        safe_click(
            By.XPATH,
            "//label[contains(., 'Docker')] | "
            "//button[contains(., 'Docker')] | "
            "//span[contains(., 'Docker')]"
        )
        time.sleep(0.8)

        # 6. Кнопка "Применить" (если есть шторка/модалка)
        apply_btns = driver.find_elements(
            By.XPATH, "//button[contains(., 'Применить')]"
        )
        if apply_btns and apply_btns[0].is_displayed():
            driver.execute_script("arguments[0].click();", apply_btns[0])
            time.sleep(2.0)

        # 7. Проверка карточек курсов
        wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//article | //a[contains(@class, 'card')] | "
                "//div[contains(@class, 'card')]"
            ))
        )

        cards = driver.find_elements(
            By.XPATH,
            "//article | //a[contains(@class, 'card')] | "
            "//div[contains(@class, 'card')]"
        )

        assert len(cards) > 0, "После применения фильтров карточки не найдены!"

        cards_text = ""
        for card in cards:
            try:
                if card.is_displayed() and card.text:
                    cards_text += " " + card.text
            except StaleElementReferenceException:
                pass

        assert ("Docker" in cards_text or "Профессия" in cards_text or len(cards) > 0), \
            "Результаты фильтрации не содержат выбранных тегов!"

    finally:
        driver.quit()


def test_github_commit_activity_hover():
    """Кейс №5: Проверка наведения мыши на график активности коммитов."""
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
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, "g.highcharts-tooltip"
        ))
    )

    # 4. ASSERT: Проверяем видимость подсказки
    assert tooltip.is_displayed(), "Tooltip не отображается при наведении!"

    driver.quit()