import os
import requests
from bs4 import BeautifulSoup
import hashlib
import json

# === Настройки ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не заданы в переменных окружения!")

URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"

SEEN_FILE = "seen_ads.json"
seen_ads = set()

# === Загрузка истории объявлений ===
if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            seen_ads = set(json.load(f))
        print(f"📂 Загружено {len(seen_ads)} старых объявлений из {SEEN_FILE}")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки {SEEN_FILE}: {e}")

def get_ad_hash(title, url):
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

def get_latest_ads():
    print(f"🌐 Загружаем страницу: {URL}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    ads = soup.select('table.list tr[id^=tr_]')
    print(f"🔍 Найдено {len(ads)} объявлений на странице.")

    new_ads = []
    for ad in ads:
        link_tag = ad.select_one('a[href]')
        if not link_tag:
            continue

        title = link_tag.text.strip()
        relative_url = link_tag['href']
        full_url = 'https://www.ss.com' + relative_url

        ad_hash = get_ad_hash(title, full_url)
        if ad_hash not in seen_ads:
            seen_ads.add(ad_hash)
            new_ads.append((title, full_url))

    return new_ads

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)

    if r.status_code != 200:
        print(f"❌ Ошибка отправки: {r.status_code}, ответ: {r.text}")
    else:
        print("✅ Сообщение отправлено в Telegram.")

if __name__ == "__main__":
    print("▶️ Бот запущен.")
    try:
        ads = get_latest_ads()
        if ads:
            send_telegram_message(f"🔔 Найдено {len(ads)} новых объявлений!")
            for title, url in ads:
                msg = f"{title}\n{url}"
                send_telegram_message(msg)
                print(f"📬 Отправлено: {title}")
        else:
            print("ℹ️ Новых объявлений нет.")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")

    # Сохраняем историю
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_ads), f)
        print(f"💾 Сохранено {len(seen_ads)} объявлений в {SEEN_FILE}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения {SEEN_FILE}: {e}")
