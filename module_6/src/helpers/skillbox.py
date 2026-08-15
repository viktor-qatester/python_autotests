"""Действия на Skillbox: фильтры программ на /code/."""
import re

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.helpers import ui
from src.helpers.logger import logger

CODE_URL = "https://skillbox.ru/code/"
SELECTED_TOPIC = "Docker"
MODAL_XPATH = "//div[contains(@class, 'programs-filter-modal')]"
MODAL_CSS = (By.CSS_SELECTOR, "div.programs-filter-modal")
COOKIE_BUTTON = (
    By.XPATH,
    "//button[contains(., 'Согласен') or contains(., 'Принять')]",
)
# На десктопе видна кнопка «Фильтры» (--desktop), на узком экране — иконка
# (--mobile). Общий селектор .programs-filter-mobile__button может вернуть
# скрытую иконку.
FILTERS_BUTTON = (
    By.XPATH,
    "//button[contains(@class, 'programs-filter-mobile__button--desktop') "
    "and contains(., 'Фильтры')]"
    " | "
    "//button[contains(@class, 'programs-filter-mobile__button--mobile') "
    "and @aria-label='Показать фильтр']",
)
PROFESSION_MODAL = (
    By.XPATH,
    f"{MODAL_XPATH}//button[contains(@class, 'programs-filter-group__tab') "
    f"and contains(., 'Профессия')]",
)
PROFESSION_DESKTOP = (
    By.XPATH,
    "//button[contains(@class, 'programs-filter-desktop__tab') "
    "and contains(., 'Профессия')]",
)
# data-* нет. На десктопе пункт — li.ui-round-select__item («от 6 до 12 мес.»),
# не button. В модалке по-прежнему button.
DURATION_6_12_MODAL = (
    By.XPATH,
    f"{MODAL_XPATH}//button[contains(., '6') and contains(., '12')]",
)
DURATION_6_12_DESKTOP = (
    By.XPATH,
    "//li[contains(@class, 'ui-round-select__item') "
    "and contains(., '6') and contains(., '12')]",
)
DURATION_TRIGGER = (
    By.XPATH,
    "//div[contains(@class, 'ui-round-select')]"
    "[contains(., 'Длительность')]"
    "//button[contains(@class, 'ui-round-select__field') "
    "or contains(@aria-label, 'Открыть')]",
)
DOCKER_MODAL = (
    By.XPATH,
    f"{MODAL_XPATH}//button[contains(@class, 'programs-filter-group__tab') "
    f"and contains(., 'Docker')]",
)
DOCKER_DESKTOP = (
    By.XPATH,
    "//li[contains(@class, 'ui-round-select__item') "
    "and contains(., 'Docker')]",
)
TOPIC_TRIGGER = (
    By.XPATH,
    "//div[contains(@class, 'ui-round-select')]"
    "[contains(., 'Тематика')]"
    "//button[contains(@class, 'ui-round-select__field') "
    "or contains(@aria-label, 'Открыть')]",
)
APPLY_BUTTON = (
    By.CSS_SELECTOR,
    "div.programs-filter-modal__confirm button.ui-button--filled-main",
)
CARD_XPATH = "//article | //a[contains(@class, 'card')]"


@allure.step("Открыть каталог курсов Skillbox /code/")
def open_code_catalog(driver):
    ui.open_page(driver, CODE_URL)


@allure.step("Закрыть cookie-баннер, если он есть")
def close_cookie_banner(driver):
    logger.info("Проверяем наличие cookie-баннера")
    try:
        button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(COOKIE_BUTTON)
        )
        if button.is_displayed():
            logger.info("Закрываем cookie-баннер")
            driver.execute_script("arguments[0].click();", button)
    except TimeoutException:
        logger.info("Cookie-баннер не появился")


def _modal_visible(driver):
    return any(el.is_displayed() for el in driver.find_elements(*MODAL_CSS))


def _desktop_filters_visible(driver):
    """Как у куратора на 1920×1080: панель Профессия / Длительность / Тематика."""
    tabs = driver.find_elements(*PROFESSION_DESKTOP)
    bars = driver.find_elements(By.CSS_SELECTOR, "div.programs-filter-desktop")
    return any(el.is_displayed() for el in list(tabs) + list(bars))


def _filters_button_displayed(driver):
    for el in driver.find_elements(*FILTERS_BUTTON):
        if el.is_displayed() and el.size.get("width", 0) > 0:
            return True
    return False


PAGE_HEADING = (
    By.XPATH,
    "//h1[contains(., 'Программирование')] | //h2[contains(., 'Программирование')]",
)


def _profession_selected(classes):
    """На десктопе выбранная «Профессия» — чёрная кнопка, не ui-tab--active."""
    parts = (classes or "").split()
    if "ui-tab--active" in parts:
        return True
    if any(marker in parts for marker in ("ui-tab--filled", "ui-tab--black")):
        return True
    # До клика: ui-tab--stroke-additional-bg. После — заливка, stroke-класса нет.
    return (
        "programs-filter-desktop__tab" in parts
        and "ui-tab--stroke-additional-bg" not in parts
    )


def _dismiss_filter_poppers(driver):
    """v-popper показывает тултип над «Профессия» и блокирует «Длительность»."""
    logger.info("Закрываем тултип: клик по заголовку страницы")
    try:
        heading = driver.find_element(*PAGE_HEADING)
        ui.scroll_to(driver, heading)
        heading.click()
    except Exception:
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
    try:
        WebDriverWait(driver, 3).until(
            EC.invisibility_of_element_located((
                By.CSS_SELECTOR, ".v-popper__popper--shown",
            ))
        )
    except TimeoutException:
        logger.info("Тултип v-popper не скрылся за 3 с — продолжаем")


@allure.step("Клик по фильтру (scroll + JS)")
def click_in_modal(driver, element):
    """Скролл + JS-клик: футер модалки / соседние блоки не перехватывают клик."""
    logger.info("Кликаем элемент фильтра")
    ui.scroll_to(driver, element)
    ui.js_click(driver, element)


@allure.step("Открыть фильтры программ")
def open_filters_modal(driver, timeout=20):
    """На 1920px Skillbox показывает десктоп-панель, модалка — на узком экране."""
    logger.info("Открываем фильтры программ")
    ui.wait_until(
        driver,
        lambda d: _desktop_filters_visible(d) or _filters_button_displayed(d),
        timeout=timeout,
        description="появились фильтры (десктоп-панель или кнопка)",
    )
    if _desktop_filters_visible(driver):
        logger.info("Десктоп-панель фильтров уже видна, модалку не открываем")
        return

    filters_btn = ui.wait_present(driver, FILTERS_BUTTON, timeout)
    ui.scroll_to(driver, filters_btn)
    try:
        clickable = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(FILTERS_BUTTON)
        )
        clickable.click()
    except TimeoutException:
        logger.info("Кнопка «Фильтры» некликабельна — кликаем через JS")
        ui.js_click(driver, filters_btn)
    ui.wait_visible(driver, MODAL_CSS, timeout)


def is_profession_selected(element):
    return _profession_selected(element.get_attribute("class"))


@allure.step("Выбрать вкладку «Профессия»")
def select_profession(driver, timeout=20):
    locator = (
        PROFESSION_DESKTOP if _desktop_filters_visible(driver) else PROFESSION_MODAL
    )
    profession_btn = ui.wait_clickable(driver, locator, timeout)
    ui.scroll_to(driver, profession_btn)
    logger.info("Кликаем вкладку «Профессия»")
    profession_btn.click()

    def is_selected(d):
        for el in d.find_elements(*locator):
            if _profession_selected(el.get_attribute("class")):
                return el
        return False

    selected = ui.wait_until(
        driver,
        is_selected,
        timeout=timeout,
        description="фильтр «Профессия» применился",
    )
    logger.info("Классы вкладки Профессия: %s", selected.get_attribute("class"))
    _dismiss_filter_poppers(driver)
    return selected


def _pick_round_select(
    driver, trigger_locator, option_locator, expected_text=None, timeout=20
):
    """Нативный клик: JS-клик не раскрывает ui-round-select."""
    _dismiss_filter_poppers(driver)
    trigger = ui.wait_clickable(driver, trigger_locator, timeout)
    ui.scroll_to(driver, trigger)
    logger.info("Открываем выпадающий список фильтра")
    trigger.click()
    option = ui.wait_clickable(driver, option_locator, timeout)
    logger.info("Выбираем пункт списка")
    option.click()
    if expected_text:
        ui.wait_until(
            driver,
            lambda d: any(
                expected_text.lower() in (el.text or "").lower()
                for el in d.find_elements(
                    By.CSS_SELECTOR, "button.ui-round-select__field"
                )
            ),
            timeout=timeout,
            description=f"в фильтре отобразилось «{expected_text}»",
        )


@allure.step("Выбрать длительность 6–12 месяцев")
def select_duration_6_12(driver, timeout=20):
    if not _modal_visible(driver):
        _pick_round_select(
            driver, DURATION_TRIGGER, DURATION_6_12_DESKTOP, "6", timeout
        )
        return
    duration_btn = ui.wait_clickable(driver, DURATION_6_12_MODAL, timeout)
    click_in_modal(driver, duration_btn)


@allure.step("Выбрать тематику Docker")
def select_topic_docker(driver, timeout=20):
    if not _modal_visible(driver):
        _pick_round_select(
            driver, TOPIC_TRIGGER, DOCKER_DESKTOP, timeout=timeout
        )
        return
    docker_btn = ui.wait_present(driver, DOCKER_MODAL, timeout)
    click_in_modal(driver, docker_btn)


@allure.step("Применить фильтры")
def apply_filters(driver, timeout=20):
    if not _modal_visible(driver):
        logger.info("Модалки нет — фильтры на десктопе применяются сразу")
        return
    apply_btn = ui.wait_clickable(driver, APPLY_BUTTON, timeout)
    click_in_modal(driver, apply_btn)
    ui.wait_invisible(driver, MODAL_CSS, timeout)


@allure.step("Дождаться карточек программ")
def wait_course_cards(driver, timeout=20):
    logger.info("Ждём карточки программ после фильтров")

    def cards_ready(d):
        cards = [
            c for c in d.find_elements(By.XPATH, CARD_XPATH)
            if c.is_displayed() and c.text.strip()
        ]
        if not cards:
            return False
        text = " ".join(c.text for c in cards)
        if "профессия" not in text.lower():
            return False
        months = months_from_text(text)
        return bool(months) and all(6 <= m <= 12 for m in months)

    ui.wait_until(
        driver,
        cards_ready,
        timeout=timeout,
        description="карточки обновились под фильтры 6–12 мес.",
    )
    return driver.find_elements(By.XPATH, CARD_XPATH)


def visible_cards_text(cards):
    return " ".join(
        card.text for card in cards if card.is_displayed() and card.text
    )


def months_from_text(text):
    return [int(m) for m in re.findall(r"(\d+)\s*месяц", text)]
