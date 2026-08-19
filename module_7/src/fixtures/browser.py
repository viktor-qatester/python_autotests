import pytest
from playwright.sync_api import sync_playwright

from src.helpers.logger import logger

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


@pytest.fixture
def page():
    logger.info("Запускаем браузер Chromium")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT}
        )
        page = context.new_page()
        page.set_default_timeout(20_000)

        yield page

        logger.info("Закрываем браузер")
        context.close()
        browser.close()
