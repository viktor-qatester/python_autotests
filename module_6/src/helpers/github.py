"""Действия на GitHub: Issues, Advanced Search, график commit-activity."""
import re

import allure
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.helpers import ui
from src.helpers.logger import logger

ISSUES_URL = "https://github.com/microsoft/vscode/issues"
ISSUES_SEARCH_QUERY = "in:title bug sort:created-desc"
ISSUES_SEARCH_URL = (
    "https://github.com/microsoft/vscode/issues"
    "?q=is%3Aissue+in%3Atitle+bug+sort%3Acreated-desc"
)
ADVANCED_SEARCH_URL = "https://github.com/search/advanced"
COMMIT_ACTIVITY_URL = (
    "https://github.com/microsoft/vscode/graphs/commit-activity"
)

# data-testid стабилен; PinnedIssue исключаем, чтобы закреплённые карточки
# не попадали в проверку заголовков результатов поиска.
ISSUE_TITLE_XPATH = (
    "//a[@data-testid='issue-pr-title-link' "
    "and not(ancestor::div[contains(@class, 'PinnedIssue')])]"
)
SEARCH_INPUT = (By.ID, "repository-input")
QUERY_BUILDER = (By.ID, "query-builder-test")
AUTHOR_BUTTON = (By.CSS_SELECTOR, "button[data-testid='authors-anchor-button']")
AUTHOR_INPUT = (By.CSS_SELECTOR, "input[placeholder='Filter authors']")
LANGUAGE_SELECT = (By.ID, "search_language")
PYTHON_OPTION = (By.XPATH, "//option[@value='Python']")
STARS_INPUT = (By.ID, "search_stars")
FILENAME_INPUT = (By.ID, "search_filename")
ADVANCED_SEARCH_BUTTON = (
    By.XPATH,
    "//*[@id='search_form']/div[2]/div/div/button | "
    "//*[@id='search_form']//button[@type='submit']",
)
STARGAZERS_LINKS = (By.CSS_SELECTOR, "a[href*='stargazers']")
CHART_POINT = (By.CSS_SELECTOR, ".highcharts-point")
CHART_TOOLTIP = (By.CSS_SELECTOR, "g.highcharts-tooltip")
AUTOCOMPLETE_LISTBOX = (By.CSS_SELECTOR, "[role='listbox']")


def issue_title_texts(driver):
    """Тексты заголовков из результатов поиска (без pinned и без PR).

    Возвращаем строки, а не WebElement: React на GitHub перерисовывает список,
    и обращение к .text у уже найденного элемента даёт StaleElementReference.
    Без allure.step: функция вызывается внутри wait.until в цикле опроса.
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


def _search_applied(driver):
    url = driver.current_url.lower()
    try:
        value = (
            driver.find_element(*SEARCH_INPUT).get_attribute("value") or ""
        ).lower()
    except Exception:
        value = ""
    return ("in:title" in value or "in%3atitle" in url) and (
        "bug" in value or "bug" in url
    )


def _titles_all_contain_bug(driver):
    titles = issue_title_texts(driver)
    return bool(titles) and all("bug" in t.lower() for t in titles)


def search_query_value(driver):
    """Значение строки поиска Issues. Без шага Allure — опрашивается в wait."""
    try:
        return driver.find_element(*QUERY_BUILDER).get_attribute("value") or ""
    except Exception:
        return ""


def python_in_url(driver):
    url = driver.current_url
    return (
        "Python" in url
        or "language%3APython" in url
        or "l=Python" in url
    )


@allure.step("Открыть страницу Issues репозитория vscode")
def open_issues(driver):
    ui.open_page(driver, ISSUES_URL)


@allure.step("Найти issues по запросу in:title bug")
def search_issues_in_title_bug(driver, timeout=20):
    logger.info("Вводим запрос Issues: %s", ISSUES_SEARCH_QUERY)
    search_input = ui.wait_clickable(driver, SEARCH_INPUT, timeout)
    search_input.click()
    search_input.send_keys(Keys.CONTROL, "a")
    search_input.send_keys(Keys.BACKSPACE)
    search_input.send_keys(ISSUES_SEARCH_QUERY)
    # Escape закрывает дропдаун автокомплита, чтобы Enter отправил форму,
    # а не выбрал подсказку (например, "Copilot Agent Host...").
    logger.info("Закрываем автокомплит (Escape) и отправляем форму")
    search_input.send_keys(Keys.ESCAPE)
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located(AUTOCOMPLETE_LISTBOX)
        )
    except TimeoutException:
        logger.info("Автокомплит не скрылся за 5 с, отправляем Enter")
    search_input.send_keys(Keys.ENTER)

    try:
        ui.wait_until(
            driver,
            _search_applied,
            timeout=timeout,
            description="поиск Issues применился",
        )
    except TimeoutException:
        logger.info("Автокомплит перехватил Enter — применяем запрос через URL")
        ui.open_page(driver, ISSUES_SEARCH_URL)
        ui.wait_until(
            driver,
            _search_applied,
            timeout=timeout,
            description="поиск Issues применился по URL",
        )

    search_input = ui.wait_present(driver, SEARCH_INPUT, timeout)
    search_value = (search_input.get_attribute("value") or "").lower()
    url_lower = driver.current_url.lower()
    if "created" not in url_lower and "created" not in search_value:
        logger.info("Сортировка не применилась — повторяем запрос через URL")
        ui.open_page(driver, ISSUES_SEARCH_URL)
        search_input = ui.wait_present(driver, SEARCH_INPUT, timeout)
        search_value = (search_input.get_attribute("value") or "").lower()

    assert "in:title" in search_value, (
        "Фильтр in:title не отражён в поле поиска после применения!"
    )

    try:
        ui.wait_until(
            driver,
            _titles_all_contain_bug,
            timeout=timeout,
            description="все заголовки issues содержат bug",
        )
    except TimeoutException:
        titles = issue_title_texts(driver)
        bad = [t for t in titles if "bug" not in t.lower()]
        raise AssertionError(
            f"Не все заголовки содержат 'bug'. Всего: {len(titles)}. "
            f"Без 'bug': {bad}"
        )


@allure.step("Открыть фильтр Author")
def open_author_filter(driver, timeout=20):
    ui.click(driver, AUTHOR_BUTTON, timeout)


@allure.step("Ввести автора {author} в фильтр")
def type_author(driver, author, timeout=20):
    logger.info("Вводим автора %s", author)
    author_input = ui.wait_clickable(driver, AUTHOR_INPUT, timeout)
    author_input.send_keys(author)


@allure.step("Дождаться пункта автора {author} в списке")
def wait_author_option(driver, author, timeout=20):
    option = (By.XPATH, f"//*[@role='option'][contains(., '{author}')]")
    return ui.wait_clickable(driver, option, timeout)


@allure.step("Выбрать автора {author} из списка")
def click_author_option(driver, author, timeout=20):
    from selenium.common.exceptions import StaleElementReferenceException

    option = (By.XPATH, f"//*[@role='option'][contains(., '{author}')]")
    logger.info("Выбираем автора %s из списка", author)

    def click_option(d):
        for el in d.find_elements(*option):
            try:
                if el.is_displayed():
                    el.click()
                    return True
            except StaleElementReferenceException:
                continue
        return False

    ui.wait_until(
        driver,
        click_option,
        timeout=timeout,
        description=f"клик по автору {author}",
    )


@allure.step("Дождаться применения фильтра автора {author}")
def wait_author_applied(driver, author, timeout=20):
    logger.info("Ждём, пока автор %s появится в поиске или URL", author)

    def applied(d):
        return author in search_query_value(d) or author in d.current_url

    ui.wait_until(
        driver,
        applied,
        timeout=timeout,
        description=f"фильтр автора {author} применился",
    )


@allure.step("Открыть расширенный поиск GitHub")
def open_advanced_search(driver):
    ui.open_page(driver, ADVANCED_SEARCH_URL)


@allure.step("Выбрать язык Python")
def select_language_python(driver, timeout=20):
    language_field = ui.wait_clickable(driver, LANGUAGE_SELECT, timeout)
    language_field.click()
    python_option = ui.wait_clickable(driver, PYTHON_OPTION, timeout)
    python_option.click()
    return language_field


@allure.step("Заполнить звёзды и имя файла, отправить форму")
def fill_stars_filename_and_submit(
    driver,
    stars=">20000",
    filename="environment.yml",
    timeout=20,
):
    logger.info("Вводим stars=%s, filename=%s и отправляем форму", stars, filename)
    stars_input = ui.wait_present(driver, STARS_INPUT, timeout)
    stars_input.send_keys(stars)
    filename_input = ui.wait_present(driver, FILENAME_INPUT, timeout)
    filename_input.send_keys(filename)
    search_button = ui.wait_clickable(driver, ADVANCED_SEARCH_BUTTON, timeout)
    ui.scroll_to(driver, search_button)
    ui.js_click(driver, search_button)
    ui.wait_until(
        driver,
        python_in_url,
        timeout=timeout,
        description="в URL появились параметры языка Python",
    )


def parse_star_count(text):
    text = text.strip().lower().replace(",", "")
    if text.endswith("k"):
        return int(float(text[:-1]) * 1_000)
    if text.endswith("m"):
        return int(float(text[:-1]) * 1_000_000)
    return int(text)


@allure.step("Считать количество звёзд из результатов поиска")
def star_counts_from_results(driver, timeout=20):
    logger.info("Читаем количество звёзд у репозиториев")
    star_links = WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(STARGAZERS_LINKS)
    )
    return [
        parse_star_count(link.text) for link in star_links if link.text.strip()
    ]


@allure.step("Открыть график commit-activity")
def open_commit_activity(driver):
    ui.open_page(driver, COMMIT_ACTIVITY_URL)


@allure.step("Найти точку графика commit-activity")
def chart_point(driver, timeout=20):
    return ui.wait_present(driver, CHART_POINT, timeout)


def tooltip_elements(driver):
    return driver.find_elements(*CHART_TOOLTIP)


@allure.step("Навести курсор на точку графика")
def hover_chart_point(driver, point):
    ui.hover(driver, point)


@allure.step("Дождаться тултипа графика")
def wait_tooltip_visible(driver, timeout=20):
    return ui.wait_visible(driver, CHART_TOOLTIP, timeout)
