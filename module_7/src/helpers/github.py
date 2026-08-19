"""Действия на GitHub: Issues, Advanced Search, график commit-activity."""
import re

import allure
from playwright.sync_api import expect

from src.helpers import ui
from src.helpers.logger import logger

ISSUES_URL = "https://github.com/microsoft/vscode/issues"
ADVANCED_SEARCH_URL = "https://github.com/search/advanced"
COMMIT_ACTIVITY_URL = "https://github.com/microsoft/vscode/graphs/commit-activity"

SEARCH_INPUT = "#repository-input"
ISSUE_TITLE_LINKS = "a[data-testid='issue-pr-title-link']"
AUTHOR_BUTTON = "button[data-testid='authors-anchor-button']"
AUTHOR_INPUT = "input[placeholder='Filter authors']"
LANGUAGE_SELECT = "#search_language"
STARS_INPUT = "#search_stars"
FILENAME_INPUT = "#search_filename"
ADVANCED_SEARCH_BUTTON = "#adv_code_search button[type='submit']"
STARGAZERS_LINKS = "a[href*='stargazers']"
CHART_POINT = ".highcharts-point"
CHART_TOOLTIP = "g.highcharts-tooltip"
CHART_TOOLTIP_TEXT = "div.highcharts-tooltip"


@allure.step("Открыть страницу Issues репозитория vscode")
def open_issues(page):
    ui.open_page(page, ISSUES_URL)


def issue_titles(page):
    """Заголовки issues из результатов поиска (закреплённые issues и PR исключены)."""
    return page.locator(ISSUE_TITLE_LINKS).evaluate_all(
        "els => els.filter(e => /\\/issues\\/\\d+$/.test(e.href) "
        "&& !e.closest('[class*=PinnedIssue]'))"
        ".map(e => e.textContent.trim())"
    )


@allure.step("Найти issues по запросу in:title {keyword}")
def search_issues_in_title(page, keyword):
    logger.info("Ищем issues по запросу in:title %s", keyword)
    search_input = page.locator(SEARCH_INPUT)
    search_input.click()
    search_input.fill(f"in:title {keyword}")
    search_input.press("Escape")
    search_input.press("Enter")
    expect(page).to_have_url(re.compile(r"in(:|%3A)title", re.I))
    # Ждём, пока React перерисует список: старые заголовки исчезнут,
    # а все новые будут содержать искомое слово.
    page.wait_for_function(
        """(keyword) => {
            const links = Array.from(
                document.querySelectorAll("a[data-testid='issue-pr-title-link']")
            ).filter(e => /\\/issues\\/\\d+$/.test(e.href) && !e.closest('[class*=PinnedIssue]'));
            return links.length > 0
                && links.every(e => e.textContent.toLowerCase().includes(keyword));
        }""",
        arg=keyword,
    )


@allure.step("Открыть фильтр Author")
def open_author_filter(page):
    page.locator(AUTHOR_BUTTON).click()


def search_query_value(page):
    return page.locator(SEARCH_INPUT).input_value()


@allure.step("Выбрать автора {author} из списка")
def select_author(page, author):
    logger.info("Вводим и выбираем автора %s", author)
    page.locator(AUTHOR_INPUT).fill(author)
    page.get_by_role("option", name=author).first.click()
    expect(page).to_have_url(re.compile(author, re.I))


@allure.step("Открыть расширенный поиск GitHub")
def open_advanced_search(page):
    ui.open_page(page, ADVANCED_SEARCH_URL)


@allure.step("Выбрать язык Python")
def select_language_python(page):
    page.locator(LANGUAGE_SELECT).select_option("Python")


@allure.step("Заполнить звёзды и имя файла, отправить форму")
def fill_stars_filename_and_submit(page, stars=">20000", filename="environment.yml"):
    logger.info("Вводим stars=%s, filename=%s", stars, filename)
    page.locator(STARS_INPUT).fill(stars)
    page.locator(FILENAME_INPUT).fill(filename)
    page.locator(ADVANCED_SEARCH_BUTTON).click()
    expect(page).to_have_url(re.compile("language", re.I))


def parse_star_count(text):
    text = text.strip().lower().replace(",", "")
    if text.endswith("k"):
        return int(float(text[:-1]) * 1_000)
    if text.endswith("m"):
        return int(float(text[:-1]) * 1_000_000)
    return int(text)


@allure.step("Считать количество звёзд из результатов поиска")
def star_counts_from_results(page):
    texts = page.locator(STARGAZERS_LINKS).all_inner_texts()
    return [parse_star_count(text) for text in texts if text.strip()]


@allure.step("Открыть график commit-activity")
def open_commit_activity(page):
    ui.open_page(page, COMMIT_ACTIVITY_URL)


def chart_point(page):
    return page.locator(CHART_POINT).first


def chart_tooltip(page):
    return page.locator(CHART_TOOLTIP)


def tooltip_text(page):
    return page.locator(CHART_TOOLTIP_TEXT).inner_text()


@allure.step("Навести курсор на точку графика")
def hover_chart_point(point):
    point.hover()
