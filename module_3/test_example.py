from selenium.webdriver.common.by import By  # Импортируем By для выбора стратегий поиска

class TestExample:  # Наш тестовый класс (Test Suite)

    def test_find_elements(self, set_up_browser):  # Тестовый метод (Test Case)
        # 1. Принимаем браузер из фикстуры и сохраняем в удобную переменную driver
        driver = set_up_browser
        
        # 2. Переходим по адресу учебного стенда
        driver.get("https://the-internet.herokuapp.com/login")
        
        # 3. Находим поле ввода Username по ID и вводим логин
        username_input = driver.find_element(By.ID, "username")
        username_input.send_keys("tomsmith")
        
        # 4. Находим поле ввода Password по ID и вводим пароль
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys("SuperSecretPassword!")
        
        # 5. Находим кнопку Login по CSS-селектору и кликаем по ней
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # 6. Проверяем, что текущий URL изменился на ожидаемый адрес защищенной зоны
        expected_url = "https://the-internet.herokuapp.com/secure"
        assert driver.current_url == expected_url, f"Пользователь не перенаправлен! Текущий URL: {driver.current_url}"
        
        # 7. Заглушка для точки останова (оставляем, чтобы при дебаге посмотреть на финальное состояние)
        pass

