import os
import requests
from bs4 import BeautifulSoup
import hashlib

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения")

URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
sent_hashes = set()

def get_ad_hash(title, url):
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

def get_latest_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    ads = soup.select('table.list tr[id^=tr_]')
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
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"❌ Ошибка отправки: {r.text}")

if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    try:
        ads = get_latest_ads()
        for title, url in ads:
            message = f"🔔 Новое объявление:\n{title}\n{url}"
            send_telegram_message(message)
            print(f"📬 Отправлено: {title}")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
