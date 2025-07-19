import os
import requests
from bs4 import BeautifulSoup
import hashlib
import sys

# --- Конфигурация ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"

# --- Проверка переменных окружения ---
if not TELEGRAM_TOKEN or not CHAT_ID:
    print("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения.")
    sys.exit(1)
else:
    print(f"✅ TELEGRAM_TOKEN и CHAT_ID получены. (CHAT_ID={CHAT_ID})")

# --- Хранилище отправленных объявлений ---
sent_hashes = set()

def get_ad_hash(title, url):
    """Создаём хэш для объявления по title + url."""
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

def get_latest_ads():
    """Парсим страницу и ищем новые объявления."""
    print(f"🌐 Загружаем страницу: {URL}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка загрузки страницы: {e}")
        return []

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
        if ad_hash not in sent_hashes:
            sent_hashes.add(ad_hash)
            print(f"➕ Новое объявление: {title} ({full_url})")
            new_ads.append((title, full_url))

    if not new_ads:
        print("ℹ️ Новых объявлений нет.")
    return new_ads

def send_telegram_message(text):
    """Отправляем сообщение в Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}

    print(f"📤 Отправка в Telegram: {text[:50]}...")
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            print("✅ Сообщение отправлено.")
        else:
            print(f"❌ Ошибка отправки: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Ошибка при запросе к Telegram API: {e}")

if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    try:
        ads = get_latest_ads()
        for title, url in ads:
            message = f"🔔 Новое объявление:\n{title}\n{url}"
            send_telegram_message(message)
    except Exception as e:
        print(f"⚠️ Неожиданная ошибка: {e}")
