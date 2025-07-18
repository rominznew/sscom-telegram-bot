import os
import requests

# Получаем токен и ID из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    print("➡️ Ответ Telegram API:", r.text)
    return r.status_code

if __name__ == "__main__":
    print("▶️ Тест отправки сообщения...")
    code = send_telegram_message("✅ Привет! Это тестовое сообщение от GitHub Actions или твоего бота.")
    if code == 200:
        print("🎉 Сообщение успешно отправлено!")
    else:
        print("❌ Ошибка отправки.")
