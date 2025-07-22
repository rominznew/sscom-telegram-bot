import os
import requests
from bs4 import BeautifulSoup
import hashlib
import json

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
SEEN_FILE = "seen_ads.json"

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения")

# --- Работа с seen_ads.json ---
def load_seen_ads():
    if not os.path.exists(SEEN_FILE):
        print("⚠️ Файл seen_ads.json не найден. Создаём пустой []")
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception as e:
        print(f"⚠️ Ошибка чтения {SEEN_FILE}: {e}. Создаём пустой файл.")
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return set()

def save_seen_ads(seen_ads):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ads), f, ensure_ascii=False, indent=2)
    print(f"💾 Сохранено {len(seen_ads)} объявлений в {SEEN_FILE}")

# --- Хэш объявления (для уникальности) ---
def get_ad_hash(title, url):
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

# --- Получаем свежие объявления ---
def get_latest_ads(seen_ads):
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"🌐 Загружаем страницу: {URL}")
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    ads = soup.select('table#page_main table.list tr[id^=tr_] a[href]')
    print(f"🔍 Найдено {len(ads)} объявлений (всего на странице).")

    new_ads = []
    for link_tag in ads:
        title = link_tag.text.strip()
        relative_url = link_tag['href']
        full_url = 'https://www.ss.com' + relative_url
        ad_hash = get_ad_hash(title, full_url)

        if ad_hash not in seen_ads:
            seen_ads.add(ad_hash)
            new_ads.append((title, full_url))

    print(f"🆕 Найдено {len(new_ads)} новых объявлений.")
    return new_ads, seen_ads

# --- Отправка в Telegram ---
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    if r.status_code == 200:
        print(f"📩 Уведомление отправлено: {text[:50]}...")
    else:
        print(f"❌ Ошибка отправки в Telegram: {r.text}")

# --- Основной запуск ---
if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    try:
        seen_ads = load_seen_ads()
        ads, seen_ads = get_latest_ads(seen_ads)

        if ads:
            for title, url in ads:
                message = f"🔔 Новое объявление:\n{title}\n{url}"
                send_telegram_message(message)
            save_seen_ads(seen_ads)
        else:
            print("ℹ️ Новых объявлений нет.")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
