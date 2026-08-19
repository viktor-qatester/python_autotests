"""Общее действие Playwright: открытие страницы с логированием и шагом Allure."""
import allure

from src.helpers.logger import logger


@allure.step("Открыть страницу: {url}")
def open_page(page, url):
    logger.info("Открываем страницу %s", url)
    page.goto(url, wait_until="domcontentloaded", timeout=40_000)
