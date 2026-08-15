import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.helpers.logger import logger

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


@pytest.fixture
def browser():
    logger.info("Запускаем браузер Chrome")
    options = webdriver.ChromeOptions()
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(40)
    driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)

    yield driver

    logger.info("Закрываем браузер")
    driver.quit()
