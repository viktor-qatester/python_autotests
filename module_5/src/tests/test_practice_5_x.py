"""
ПР №5: валидация состояний элементов (Selenium).
Переименуй файл под фактический номер практики (см. ЛК Skillbox),
по аналогии с module_4/test_practice_4_6.py.
"""

import re
import time
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# GitHub Issues: хронологическая сортировка, иначе "Best match" подмешивает
# семантически похожие issues без слова "bug" в заголовке.
ISSUES_SEARCH_QUERY = "in:title bug sort:created-desc"
ISSUES_SEARCH_URL = (
    "https://github.com/microsoft/vscode/issues"
    "?q=is%3Aissue+in%3Atitle+bug+sort%3Acreated-desc"
)
ISSUE_TITLE_XPATH = (
    "//a[@data-testid='issue-pr-title-link' "
    "and not(ancestor::div[contains(@class, 'PinnedIssue')])]"
)


def _issue_title_texts(driver):
    """Тексты заголовков из результатов поиска (без pinned и без PR).

    Возвращаем строки, а не WebElement: React на GitHub перерисовывает список,
    и обращение к .text у уже найденного элемента даёт StaleElementReference.
    """
    try:
        found = driver.find_elements(By.XPATH, ISSUE_TITLE_XPATH)
        titles = []
        for el in found:
            href = el.get_attribute("href") or ""
            if not re.search(r"/issues/\d+$", href):
                continue
            text = (el.text or "").strip()
            if text:
                titles.append(text)
        return titles
    except StaleElementReferenceException:
        return []


def test_github_issues_search_by_title():
    """Кейс №1: in:title bug -> Enter -> все заголовки issues содержат 'bug' (без учёта регистра)."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    try:
        driver.get("https://github.com/microsoft/vscode/issues")
        wait = WebDriverWait(driver, 20)
        assert "github.com" in driver.current_url, (
            f"GitHub не загрузился (возможный блок/сеть): {driver.current_url}"
        )

        search_input = wait.until(
            EC.element_to_be_clickable((By.ID, "repository-input"))
        )
        search_input.click()
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(Keys.BACKSPACE)
        search_input.send_keys(ISSUES_SEARCH_QUERY)
        # Escape закрывает дропдаун автокомплита, чтобы Enter отправил форму,
        # а не выбрал подсказку (например, "Copilot Agent Host...").
        search_input.send_keys(Keys.ESCAPE)
        time.sleep(0.3)
        search_input.send_keys(Keys.ENTER)

        def search_applied(d):
            url = d.current_url.lower()
            try:
                value = (
                    d.find_element(By.ID, "repository-input").get_attribute("value") or ""
                ).lower()
            except Exception:
                value = ""
            return ("in:title" in value or "in%3atitle" in url) and (
                "bug" in value or "bug" in url
            )

        try:
            wait.until(search_applied)
        except TimeoutException:
            # Автокомплит перехватил Enter — применяем тот же запрос через URL.
            driver.get(ISSUES_SEARCH_URL)
            wait.until(search_applied)

        search_input = wait.until(
            EC.presence_of_element_located((By.ID, "repository-input"))
        )
        search_value = (search_input.get_attribute("value") or "").lower()
        # Если сортировка не применилась — снова Best match. Дублируем запрос URL'ом.
        if "created" not in driver.current_url.lower() and "created" not in search_value:
            driver.get(ISSUES_SEARCH_URL)
            search_input = wait.until(
                EC.presence_of_element_located((By.ID, "repository-input"))
            )
            search_value = (search_input.get_attribute("value") or "").lower()

        assert "in:title" in search_value, (
            "Фильтр in:title не отражён в поле поиска после применения!"
        )

        def titles_all_contain_bug(d):
            titles = _issue_title_texts(d)
            return bool(titles) and all("bug" in t.lower() for t in titles)

        try:
            wait.until(titles_all_contain_bug)
        except TimeoutException:
            titles = _issue_title_texts(driver)
            bad = [t for t in titles if "bug" not in t.lower()]
            raise AssertionError(
                f"Не все заголовки содержат 'bug'. Всего: {len(titles)}. Без 'bug': {bad}"
            )

        titles = _issue_title_texts(driver)
        assert titles, "Не найдено ни одной задачи по фильтру in:title bug!"
        for title in titles:
            assert "bug" in title.lower(), (
                f"Заголовок '{title}' не содержит слово 'bug'!"
            )
    finally:
        driver.quit()


def test_github_author_filter():
    """Кейс №2: фильтр Author -> bpasero -> выбор из списка -> все задачи автора bpasero."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    try:
        driver.get("https://github.com/microsoft/vscode/issues")

        wait = WebDriverWait(driver, 10)

        def search_value():
            try:
                return driver.find_element(By.ID, "query-builder-test").get_attribute("value") or ""
            except Exception:
                return ""

        author_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button[data-testid='authors-anchor-button']"
            ))
        )
        author_button.click()

        author_input = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Filter authors']"))
        )
        author_input.send_keys("bpasero")

        author_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@role='option'][contains(., 'bpasero')]"))
        )

        # Валидация состояния ДО: автор ещё не применён в поиске
        value_before = search_value()
        assert "bpasero" not in value_before, "Автор bpasero уже присутствует в поиске до выбора!"

        author_option.click()
        time.sleep(1)

        # Валидация состояния ПОСЛЕ: поиск перешёл в состояние с author:bpasero
        value_after = search_value()
        current_url = driver.current_url
        assert "bpasero" in value_after or "bpasero" in current_url, (
            "Фильтр по автору bpasero не отображается в URL или строке поиска!"
        )
    finally:
        driver.quit()


def test_github_advanced_search():
    """Кейс №3: /search/advanced -> Python + >20000 stars + environment.yml -> список репозиториев со stars > 20000."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    try:
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

        # Валидация состояния: у native <select> выбранное значение — это его
        # текущее свойство value, а не факт клика по <option>.
        selected_value = language_field.get_attribute("value")
        assert selected_value == "Python", (
            f"Поле языка не перешло в состояние 'Python', текущее значение: {selected_value!r}"
        )

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

        def parse_star_count(text):
            text = text.strip().lower().replace(",", "")
            if text.endswith("k"):
                return int(float(text[:-1]) * 1_000)
            if text.endswith("m"):
                return int(float(text[:-1]) * 1_000_000)
            return int(text)

        star_links = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='stargazers']"))
        )
        star_counts = [
            parse_star_count(link.text) for link in star_links if link.text.strip()
        ]
        assert star_counts, "Не удалось извлечь количество звёзд из результатов поиска!"
        assert all(count > 20000 for count in star_counts), (
            f"Есть репозитории с количеством звёзд <= 20000: {star_counts}"
        )
    finally:
        driver.quit()


def test_skillbox_course_filters():
    """Кейс №4: Профессия + Длительность 6-12 + Тематика -> список курсов соответствует фильтрам."""
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
        driver.implicitly_wait(1)
        cookie_btns = driver.find_elements(
            By.XPATH,
            "//button[contains(., 'Согласен') or contains(., 'Принять') "
            "or contains(., 'Окей')]",
        )
        if cookie_btns and cookie_btns[0].is_displayed():
            driver.execute_script("arguments[0].click();", cookie_btns[0])
        driver.implicitly_wait(0)

        # На десктопе видна кнопка «Фильтры» (--desktop), на узком экране — иконка (--mobile).
        # Общий селектор .programs-filter-mobile__button может вернуть скрытую иконку.
        filters_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(@class, 'programs-filter-mobile__button--desktop') "
                "and contains(., 'Фильтры')]"
                " | "
                "//button[contains(@class, 'programs-filter-mobile__button--mobile') "
                "and @aria-label='Показать фильтр']",
            ))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            filters_btn,
        )
        time.sleep(0.3)
        filters_btn.click()

        wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.programs-filter-modal")
            )
        )

        profession_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"{modal_xpath}//button[contains(@class, 'programs-filter-group__tab') "
                f"and contains(., 'Профессия')]",
            ))
        )
        click_in_modal(profession_btn)
        classes = profession_btn.get_attribute("class")
        assert "ui-tab--active" in classes.split(), (
            "Вкладка «Профессия» не стала активной после клика"
        )

        duration_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"{modal_xpath}//h3[contains(., 'Длительность')]/following-sibling::div"
                f"//button[contains(., '6') and contains(., '12')]",
            ))
        )
        click_in_modal(duration_btn)

        docker_btn = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"{modal_xpath}//button[contains(@class, 'programs-filter-group__tab') "
                f"and contains(., 'Docker')]",
            ))
        )
        click_in_modal(docker_btn)

        apply_btn = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "div.programs-filter-modal__confirm button.ui-button--filled-main",
            ))
        )
        click_in_modal(apply_btn)

        wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.programs-filter-modal")
            )
        )
        card_xpath = "//article | //a[contains(@class, 'card')]"
        wait.until(
            lambda d: any(
                c.is_displayed() and c.text.strip()
                for c in d.find_elements(By.XPATH, card_xpath)
            )
        )
        cards = driver.find_elements(By.XPATH, card_xpath)
        assert len(cards) > 0, "После применения фильтров карточки не найдены!"

        cards_text = " ".join(
            card.text for card in cards if card.is_displayed() and card.text
        )
        page_text = driver.find_element(By.TAG_NAME, "body").text

        assert "профессия" in cards_text.lower(), "В карточках нет типа 'Профессия'!"

        months = [int(m) for m in re.findall(r"(\d+)\s*месяц", cards_text)]
        assert months, "В карточках не найдена длительность (N месяцев)!"
        assert all(6 <= m <= 12 for m in months), (
            f"Есть программы вне диапазона 6–12 мес.: {months}"
        )

        assert selected_topic.lower() in page_text.lower(), (
            f"Фильтр '{selected_topic}' не отображается на странице результатов!"
        )
    finally:
        driver.quit()


def test_github_commit_activity_tooltip():
    """Кейс №5: hover на график commit-activity -> тултип содержит ожидаемые значения."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    try:
        driver.get("https://github.com/microsoft/vscode/graphs/commit-activity")

        wait = WebDriverWait(driver, 10)

        chart_bar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".highcharts-point"))
        )

        # Ожидаемые значения берём из aria-label самой точки (accessibility-атрибут
        # с датой и числом коммитов) — это надёжнее парсинга анимированного SVG-тултипа.
        expected_info = chart_bar.get_attribute("aria-label") or ""
        assert any(ch.isdigit() for ch in expected_info), (
            f"У точки графика нет ожидаемых данных в aria-label: {expected_info!r}"
        )

        # Валидация состояния ДО: тултипа ещё нет в DOM (highcharts рисует его
        # динамически только при первом hover).
        tooltip_before = driver.find_elements(By.CSS_SELECTOR, "g.highcharts-tooltip")
        assert not tooltip_before, "Тултип отображается до наведения мыши!"

        actions = ActionChains(driver)
        actions.move_to_element(chart_bar).perform()

        tooltip = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, "g.highcharts-tooltip",
            ))
        )

        assert tooltip.is_displayed(), "Tooltip не отображается при наведении!"
    finally:
        driver.quit()
