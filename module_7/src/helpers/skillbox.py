"""Действия на Skillbox: фильтры программ на /code/ (десктопная панель фильтров)."""
import re

import allure

from src.helpers import ui
from src.helpers.logger import logger

CODE_URL = "https://skillbox.ru/code/"
SELECTED_TOPIC = "Docker"

COOKIE_BUTTON = "button:has-text('Окей')"
PROFESSION_TAB = "button.programs-filter-desktop__tab:has-text('Профессия')"
DURATION_TRIGGER = (
    "xpath=//div[contains(@class, 'ui-round-select')][contains(., 'Длительность')]"
    "//button[contains(@class, 'ui-round-select__field')]"
)
DURATION_OPTION_6_12 = (
    "xpath=//li[contains(@class, 'ui-round-select__item') "
    "and contains(., '6') and contains(., '12')]"
)
TOPIC_TRIGGER = (
    "xpath=//div[contains(@class, 'ui-round-select')][contains(., 'Тематика')]"
    "//button[contains(@class, 'ui-round-select__field')]"
)
TOPIC_OPTION = "xpath=//li[contains(@class, 'ui-round-select__item') and contains(., '{topic}')]"
APPLY_BUTTON = "button:has-text('Применить')"
COURSE_CARD = "article.programs-gallery__card"


@allure.step("Открыть каталог курсов Skillbox /code/")
def open_code_catalog(page):
    ui.open_page(page, CODE_URL)


@allure.step("Закрыть cookie-баннер, если он есть")
def close_cookie_banner(page):
    button = page.locator(COOKIE_BUTTON)
    if button.is_visible():
        logger.info("Закрываем cookie-баннер")
        button.click()


@allure.step("Выбрать вкладку «Профессия»")
def select_profession(page):
    tab = page.locator(PROFESSION_TAB)
    tab.click()
    return tab


@allure.step("Выбрать длительность 6–12 месяцев")
def select_duration_6_12(page):
    page.locator(DURATION_TRIGGER).click()
    page.locator(DURATION_OPTION_6_12).click()


@allure.step("Выбрать тематику {topic} и применить фильтр")
def select_topic(page, topic=SELECTED_TOPIC):
    logger.info("Выбираем тематику %s", topic)
    page.locator(TOPIC_TRIGGER).click()
    page.locator(TOPIC_OPTION.format(topic=topic)).click()
    page.locator(APPLY_BUTTON).click()


@allure.step("Дождаться карточек программ")
def wait_course_cards(page):
    cards = page.locator(COURSE_CARD)
    cards.first.wait_for()
    return cards


def months_from_text(text):
    return [int(month) for month in re.findall(r"(\d+)\s*месяц", text)]
