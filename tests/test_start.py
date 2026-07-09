# Наш первый чистый автотест для главного сайта Skillbox.
# Фикстура 'browser' автоматически берется из conftest.py в корне проекта.

def test_start(browser):
    # Открываем главный сайт Skillbox
    browser.get("https://skillbox.ru/")
    
    # Проверяем, что в заголовке вкладки (Title) есть упоминание "Skillbox"
    assert "Skillbox" in browser.title
