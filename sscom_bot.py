import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==============================
# Настройки из переменных окружения
# ==============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

print("✅ TELEGRAM_TOKEN и CHAT_ID получены. (CHAT_ID=***)")
print("▶️ Бот запущен. Проверка объявлений...")


# ==============================
# Отправка сообщений в Telegram
# ==============================
def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print(f"⚠️ Ошибка Telegram API: {r.status_code} {r.text}")
        else:
            print(f"📨 Сообщение отправлено: {message[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")


# ==============================
# Парсинг объявлений
# ==============================
def get_ads():
    try:
        print(f"🌐 Загружаем страницу: {URL}")
        response = requests.get(URL, headers=HEADERS, timeout=20)

        if response.status_code != 200:
            print(f"❌ Ошибка загрузки страницы: {response.status_code}")
            return []

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Найдем таблицу объявлений
        ads = soup.select("tr[id^=tr_]")  # SS.com использует <tr id="tr_12345">
        print(f"🔍 Найдено {len(ads)} объявлений на странице.")

        # Если объявлений 0 — сохраняем HTML для отладки
        if len(ads) == 0:
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("⚠️ HTML страницы сохранен в debug.html (нет объявлений).")

        return ads

    except Exception as e:
        print(f"❌ Ошибка при парсинге: {e}")
        return []


# ==============================
# Основной код
# ==============================
ads = get_ads()

if not ads:
    print("ℹ️ Новых объявлений нет.")
else:
    send_telegram_message(f"Найдено {len(ads)} новых объявлений!")
