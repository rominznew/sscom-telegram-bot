import os
import requests
from bs4 import BeautifulSoup
import hashlib
import json

# Переменные окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SEEN_FILE = "seen_ads.json"

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения")

URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"

# Загружаем ранее отправленные объявления
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        try:
            sent_hashes = set(json.load(f))
        except json.JSONDecodeError:
            sent_hashes = set()
else:
    sent_hashes = set()

def get_ad_hash(title, url):
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

def get_latest_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"🌐 Загружаем страницу: {URL}")
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    ads = soup.select('tr[id^=tr_] a[href]')
    print(f"🔍 Найдено {len(ads)} объявлений (всего на странице).")
    new_ads = []

    for link_tag in ads:
        title = link_tag.text.strip()
        relative_url = link_tag['href']
        full_url = 'https://www.ss.com' + relative_url
        ad_hash = get_ad_hash(title, full_url)
        if ad_hash not in sent_hashes:
            sent_hashes.add(ad_hash)
            new_ads.append((title, full_url))

    print(f"🆕 Найдено {len(new_ads)} новых объявлений.")
    return new_ads

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"❌ Ошибка отправки: {r.text}")

if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    try:
        ads = get_latest_ads()
        if ads:
            for title, url in ads:
                message = f"🔔 Новое объявление:\n{title}\n{url}"
                send_telegram_message(message)
                print(f"📬 Отправлено: {title}")
        else:
            print("ℹ️ Новых объявлений нет.")
    finally:
        # Сохраняем хэши
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_hashes), f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(sent_hashes)} хэшей в {SEEN_FILE}")
