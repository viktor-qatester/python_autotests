import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# Возвращаем твой рабочий менеджер драйверов
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture()
def browser():
    # 1. SETUP: Включаем опции защиты от сетевого шума и SSL-ошибок
    options = webdriver.ChromeOptions()
    
    # Игнорируем проблемы с сертификатами сайтов и хендшейками
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--allow-insecure-localhost')
    
    # Оптимизация стабильности под Windows
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Полностью отключаем вывод лишних логов Chrome в наш терминал VS Code
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Запускаем браузер с явным указанием пути через Service (как было у тебя)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    
    # 2. Передаем управление в тест
    yield driver
    
    # 3. TEARDOWN: Чистое закрытие
    print("\nЗакрываем браузер...")
    driver.quit()
