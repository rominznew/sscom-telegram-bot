import os
import json
import requests
from bs4 import BeautifulSoup

# ==== Конфигурация ====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
SEEN_FILE = "seen_ads.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


# ==== Функции ====
def send_telegram_message(message: str):
    """Отправляет сообщение в Telegram."""
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


def get_ads():
    """Парсит список объявлений с SS.com."""
    try:
        print(f"🌐 Загружаем страницу: {URL}")
        response = requests.get(URL, headers=HEADERS, timeout=20)
        if response.status_code != 200:
            print(f"❌ Ошибка загрузки страницы: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("tr[id^=tr_]")

        ads = []
        for row in rows:
            link = row.select_one("a")
            if link and "ss.com" in link.get("href", ""):
                ads.append(link["href"])
        print(f"🔍 Найдено {len(ads)} объявлений на странице.")
        return ads
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return []


def load_seen_ads():
    """Загружает список уже обработанных объявлений."""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {SEEN_FILE}: {e}")
    return set()


def save_seen_ads(ads):
    """Сохраняет список обработанных объявлений."""
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(ads), f)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения {SEEN_FILE}: {e}")


# ==== Основной код ====
if not TELEGRAM_TOKEN or not CHAT_ID:
    print("❌ TELEGRAM_TOKEN или CHAT_ID не установлены.")
    exit(1)

print(f"✅ TELEGRAM_TOKEN и CHAT_ID получены. (CHAT_ID={CHAT_ID})")
print("▶️ Бот запущен. Проверка объявлений...")

ads = get_ads()
seen_ads = load_seen_ads()

new_ads = [ad for ad in ads if ad not in seen_ads]

if new_ads:
    message = f"Найдено {len(new_ads)} новых объявлений!\n" + "\n".join(new_ads[:5])
    send_telegram_message(message)
    save_seen_ads(seen_ads.union(new_ads))
    print(f"✅ Сохранено {len(new_ads)} новых объявлений.")
else:
    print("ℹ️ Новых объявлений нет.")
