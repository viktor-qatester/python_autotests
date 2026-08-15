"""Общие действия Selenium: ожидания, клики, ввод. Логи + шаги Allure."""
import allure
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.helpers.logger import logger

DEFAULT_TIMEOUT = 20


@allure.step("Открыть страницу: {url}")
def open_page(driver, url):
    logger.info("Открываем страницу %s", url)
    driver.get(url)


@allure.step("Дождаться кликабельного элемента")
def wait_clickable(driver, locator, timeout=DEFAULT_TIMEOUT):
    logger.info("Ждём кликабельный элемент: %s", locator)
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )


@allure.step("Дождаться появления элемента")
def wait_present(driver, locator, timeout=DEFAULT_TIMEOUT):
    logger.info("Ждём появление элемента: %s", locator)
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )


@allure.step("Дождаться видимости элемента")
def wait_visible(driver, locator, timeout=DEFAULT_TIMEOUT):
    logger.info("Ждём видимость элемента: %s", locator)
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


@allure.step("Дождаться скрытия элемента")
def wait_invisible(driver, locator, timeout=DEFAULT_TIMEOUT):
    logger.info("Ждём скрытие элемента: %s", locator)
    return WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located(locator)
    )


@allure.step("Дождаться: {description}")
def wait_until(driver, condition, timeout=DEFAULT_TIMEOUT,
               description="состояние страницы"):
    logger.info("Ждём условие: %s", description)
    return WebDriverWait(driver, timeout).until(condition)


@allure.step("Кликнуть по элементу")
def click(driver, locator, timeout=DEFAULT_TIMEOUT):
    logger.info("Кликаем по элементу: %s", locator)
    element = wait_clickable(driver, locator, timeout)
    element.click()
    return element


@allure.step("Кликнуть по найденному веб-элементу")
def click_element(element):
    logger.info("Кликаем по найденному веб-элементу")
    element.click()


@allure.step("Прокрутить элемент в видимую область")
def scroll_to(driver, element):
    logger.info("Скроллим элемент в центр экрана")
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        element,
    )


@allure.step("Кликнуть через JavaScript")
def js_click(driver, element):
    logger.info("JS-клик по элементу")
    driver.execute_script("arguments[0].click();", element)


@allure.step("Навести курсор на элемент")
def hover(driver, element):
    logger.info("Наводим курсор на элемент")
    ActionChains(driver).move_to_element(element).perform()
