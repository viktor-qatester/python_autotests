import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def test_github_issues_search():
    """Кейс №1: Поиск в Issues — in:title + bug → Enter."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    try:
        driver.get("https://github.com/microsoft/vscode/issues")
        wait = WebDriverWait(driver, 10)
        # 1. Поле поиска Issues (DevTools: input#repository-input)
        search_input = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "input#repository-input[placeholder='Search Issues']",
            ))
        )
        search_input.click()
        # 2. Дописываем in:title bug и жмём Enter
        search_input.send_keys(" in:title bug", Keys.ENTER)
        # 3. ASSERT: фильтр применился (URL или значение поля)
        wait.until(lambda d: "bug" in d.current_url)
        search_input = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "input#repository-input[placeholder='Search Issues']",
            ))
        )
        search_val = search_input.get_attribute("value") or ""
        current_url = driver.current_url
        assert (
            "in:title" in search_val
            or "in%3Atitle" in current_url
        ), "Фильтр in:title не применился!"
        assert (
            "bug" in search_val
            or "bug" in current_url
        ), "Ключевое слово bug не применилось в поиске!"
    finally:
        driver.quit()


def test_github_author_filter():
    """Кейс №2: Фильтрация по автору через выпадающее меню Author."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://github.com/microsoft/vscode/issues")

    wait = WebDriverWait(driver, 10)

    author_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class, 'authorFilterButton') or contains(., 'Author')]"
        ))
    )
    author_button.click()

    author_input = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='__primerPortalRoot__']//input | "
            "//input[@placeholder='Filter authors']"
        ))
    )
    author_input.send_keys("bpasero")
    time.sleep(1)

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
    driver.get("https://github.com/search/advanced")

    wait = WebDriverWait(driver, 10)

    language_field = wait.until(
        EC.element_to_be_clickable((By.ID, "search_language"))
    )
    language_field.click()

    python_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//option[@value='Python']"))
    )
    python_option.click()

    stars_input = wait.until(
        EC.presence_of_element_located((By.ID, "search_stars"))
    )
    stars_input.send_keys(">20000")

    filename_input = wait.until(
        EC.presence_of_element_located((By.ID, "search_filename"))
    )
    filename_input.send_keys("environment.yml")

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

    assert (
        "Python" in driver.current_url
        or "language%3APython" in driver.current_url
        or "l=Python" in driver.current_url
    ), "Параметры поиска Python не найдены в URL!"

    driver.quit()



def test_skillbox_course_filters():
    """Кейс №4: Фильтрация курсов Skillbox (Профессия + 6-12 мес + Docker)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    wait = WebDriverWait(driver, 20)
    selected_topic = "Docker"
    modal_xpath = "//div[contains(@class, 'programs-filter-modal')]"
    def click_in_modal(element):
        """Скролл + JS-клик: футер модалки не перехватывает клик."""
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element,
        )
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", element)
    try:
        driver.get("https://skillbox.ru/code/")
        # 1. Закрыть куки (если есть)
        driver.implicitly_wait(1)
        cookie_btns = driver.find_elements(
            By.XPATH,
            "//button[contains(., 'Согласен') or contains(., 'Принять')]",
        )
        if cookie_btns and cookie_btns[0].is_displayed():
            driver.execute_script("arguments[0].click();", cookie_btns[0])
        driver.implicitly_wait(0)
        # 2. Открыть «Фильтры»
        filters_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.programs-filter-mobile__button")
            )
        )
        filters_btn.click()
        # 3. Дождаться модалки
        wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.programs-filter-modal")
            )
        )
        # 4. «Профессия»
        profession_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"{modal_xpath}//button[contains(@class, 'programs-filter-group__tab') "
                f"and contains(., 'Профессия')]",
            ))
        )
        click_in_modal(profession_btn)
        # 5. «Длительность» → 6–12 мес.
        duration_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"{modal_xpath}//h3[contains(., 'Длительность')]/following-sibling::div"
                f"//button[contains(., '6') and contains(., '12')]",
            ))
        )
        click_in_modal(duration_btn)
        # 6. «Тематика» → Docker
        docker_btn = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"{modal_xpath}//button[contains(@class, 'programs-filter-group__tab') "
                f"and contains(., 'Docker')]",
            ))
        )
        click_in_modal(docker_btn)
        # 7. «Применить»
        apply_btn = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "div.programs-filter-modal__confirm button.ui-button--filled-main",
            ))
        )
        click_in_modal(apply_btn)
        # 8. Дождаться результатов
        wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.programs-filter-modal")
            )
        )
        wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//article | //a[contains(@class, 'card')]",
            ))
        )
        cards = driver.find_elements(
            By.XPATH,
            "//article | //a[contains(@class, 'card')]",
        )
        assert len(cards) > 0, "После применения фильтров карточки не найдены!"
        cards_text = " ".join(
            card.text for card in cards if card.is_displayed() and card.text
        )
        page_text = driver.find_element(By.TAG_NAME, "body").text
        # Проверка 1: только программы типа «Профессия»
        assert "профессия" in cards_text.lower(), (
            "В карточках нет типа 'Профессия'!"
        )
        # Проверка 2: длительность 6–12 месяцев
        months = [int(m) for m in re.findall(r"(\d+)\s*месяц", cards_text)]
        assert months, "В карточках не найдена длительность (N месяцев)!"
        assert all(6 <= m <= 12 for m in months), (
            f"Есть программы вне диапазона 6–12 мес.: {months}"
        )
        # Проверка 3: тематика Docker — на странице (чипы/фильтры), не в названии курса
        assert selected_topic.lower() in page_text.lower(), (
            f"Фильтр '{selected_topic}' не отображается на странице результатов!"
        )
    finally:
        driver.quit()


def test_github_commit_activity_hover():
    """Кейс №5: Проверка наведения мыши на график активности коммитов."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://github.com/microsoft/vscode/graphs/commit-activity")

    wait = WebDriverWait(driver, 10)

    chart_bar = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".highcharts-point"))
    )

    actions = ActionChains(driver)
    actions.move_to_element(chart_bar).perform()

    tooltip = wait.until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR, "g.highcharts-tooltip",
        ))
    )

    assert tooltip.is_displayed(), "Tooltip не отображается при наведении!"

    driver.quit()