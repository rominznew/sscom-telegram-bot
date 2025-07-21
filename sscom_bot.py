import os
import json
import requests
from bs4 import BeautifulSoup
import hashlib

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"

SEEN_FILE = "seen_ads.json"
sent_hashes = set()

# ---------- Функции ----------

def load_seen_ads():
    """Загрузка списка уже отправленных объявлений."""
    global sent_hashes
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                sent_hashes = set(json.load(f))
            print(f"📂 Загружено {len(sent_hashes)} старых объявлений из {SEEN_FILE}.")
        except Exception as e:
            print(f"⚠️ Ошибка чтения {SEEN_FILE}: {e}")
            sent_hashes = set()
    else:
        print("ℹ️ Файл seen_ads.json не найден, создаём новый.")

def save_seen_ads():
    """Сохранение списка объявлений."""
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_hashes), f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(sent_hashes)} объявлений в {SEEN_FILE}.")
    except Exception as e:
        print(f"❌ Ошибка сохранения {SEEN_FILE}: {e}")

def get_ad_hash(title, url):
    """Уникальный хэш объявления."""
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

def get_latest_ads():
    """Парсинг сайта."""
    print(f"🌐 Загружаем страницу: {URL}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    ads = soup.select('table[class="list"] tr[id^=tr_]')

    print(f"🔍 Найдено {len(ads)} объявлений.")
    new_ads = []

    for ad in ads:
        link_tag = ad.select_one('a[href]')
        if not link_tag:
            continue

        title = link_tag.text.strip()
        relative_url = link_tag['href']
        full_url = 'https://www.ss.com' + relative_url
        ad_hash = get_ad_hash(title, full_url)

        if ad_hash not in sent_hashes:
            sent_hashes.add(ad_hash)
            new_ads.append((title, full_url))

    return new_ads

def send_telegram_message(text):
    """Отправка сообщения в Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"❌ Ошибка отправки: {r.text}")
    else:
        print(f"📬 Сообщение отправлено: {text[:50]}...")

# ---------- MAIN ----------

if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены.")

    load_seen_ads()
    ads = get_latest_ads()

    if ads:
        send_telegram_message(f"🔔 Найдено {len(ads)} новых объявлений!")
        for title, url in ads:
            send_telegram_message(f"{title}\n{url}")
            print(f"Отправлено: {title}")
    else:
        print("ℹ️ Новых объявлений нет.")

    save_seen_ads()
