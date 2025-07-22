import os
import requests
from bs4 import BeautifulSoup
import hashlib
import json

# === Конфигурация ===
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
SEEN_FILE = "seen_ads.json"

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения")

# === Работа с хэшами ===
def get_ad_hash(title, url):
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

# === Загрузка истории ===
def load_seen_ads():
    if not os.path.exists(SEEN_FILE):
        print(f"⚠️ Файл {SEEN_FILE} не найден. Создаём новый.")
        save_seen_ads(set())
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception as e:
        print(f"⚠️ Ошибка загрузки {SEEN_FILE}: {e}")
        return set()

def save_seen_ads(seen_ads):
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_ads), f)
        print(f"💾 Сохранено {len(seen_ads)} объявлений в {SEEN_FILE}")
    except Exception as e:
        print(f"❌ Ошибка записи {SEEN_FILE}: {e}")

# === Парсинг объявлений ===
def get_latest_ads(seen_ads):
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"🌐 Загружаем страницу: {URL}")
    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        print(f"❌ Ошибка загрузки страницы: {response.status_code}")
        return [], seen_ads

    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.select('tr[id^="tr_"]')
    print(f"🔍 Найдено {len(rows)} строк с объявлениями.")

    new_ads = []

    for row in rows:
        link_tag = row.select_one('a[href*="/msg/"]')
        if not link_tag:
            continue

        title = link_tag.text.strip()
        relative_url = link_tag['href']
        full_url = 'https://www.ss.com' + relative_url if not relative_url.startswith("http") else relative_url

        ad_hash = get_ad_hash(title, full_url)
        if ad_hash not in seen_ads:
            seen_ads.add(ad_hash)
            new_ads.append((title, full_url))

    print(f"🆕 Найдено {len(new_ads)} новых объявлений.")
    return new_ads, seen_ads

# === Telegram ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"❌ Ошибка отправки: {r.text}")
    else:
        print("📨 Уведомление отправлено.")

# === Основной запуск ===
if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    seen_ads = load_seen_ads()

    try:
        ads, seen_ads = get_latest_ads(seen_ads)
        if ads:
            for title, url in ads:
                message = f"🔔 Новое объявление:\n{title}\n{url}"
                send_telegram_message(message)
                print(f"📬 Отправлено: {title}")
        else:
            print("ℹ️ Новых объявлений нет.")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")

    save_seen_ads(seen_ads)
