import requests

# Отправляем GET-запрос на тестовый сервис httpbin.org
# Этот сервис просто возвращает нам данные, которые мы ему отправили
response = requests.get("https://httpbin.org/get")

# Проверяем статус-код (200 OK означает успешный запрос)
if response.status_code == 200:
    print("УРА! Библиотека requests работает корректно через VPN!")
    print("Ответ сервера (JSON):", response.json())
else:
    print(f"Ошибка! Статус-код: {response.status_code}")
