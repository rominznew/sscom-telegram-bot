import os
import requests

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    if not token or not chat_id:
        print("Ошибка: TELEGRAM_TOKEN или CHAT_ID не заданы в переменных окружения.")
        return

    message = "Test message from GitHub Actions"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print("Сообщение успешно отправлено.")
    else:
        print(f"Ошибка при отправке сообщения: {response.status_code}")
        print("Ответ:", response.text)

if __name__ == "__main__":
    main()
