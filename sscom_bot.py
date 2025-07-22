import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup

# --- Константы ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
SEEN_FILE = "seen_ads.json"

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("❌ TELEGRAM_TOKEN или CHAT_ID не установлены в переменных окружения.")

# --- Функции для работы с JSON ---
def load_seen_ads():
    if not os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return set()
    try:
        with open(SEEN_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data)
    except json.JSONDecodeError:
        return set()

def save_seen_ads(seen_ads):
    with open(SEEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(seen_ads), f, ensure_ascii=False, indent=2)

# --- Хэш объявления ---
def get_ad_hash(title, url):
    return hashlib.md5(f"{title}-{url}".encode()).hexdigest()

# --- Парсинг сайта ---
def get_latest_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    ads = soup.select('tr[id^="tr_"] td.msga2 a')

    results = []
    for link_tag in ads:
        title = link_tag.get_text(strip=True)
        relative_url = link_tag.get('href')
        if not relative_url:
            continue
        full_url = 'https://www.ss.com' + relative_url
        ad_hash = get_ad_hash(title, full_url)
        results.append((title, full_url, ad_hash))
    return results

# --- Telegram ---
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"❌ Ошибка отправки: {r.text}")

# --- Главный блок ---
if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    seen_ads = load_seen_ads()
    print(f"📦 Уже известно {len(seen_ads)} объявлений.")

    try:
        ads = get_latest_ads()
        print(f"🔍 Найдено {len(ads)} объявлений на странице.")

        new_count = 0
        for title, url, ad_hash in ads:
            if ad_hash not in seen_ads:
                send_telegram_message(f"🔔 Новое объявление:\n{title}\n{url}")
                print(f"📬 Отправлено: {title}")
                seen_ads.add(ad_hash)
                new_count += 1

        if new_count > 0:
            save_seen_ads(seen_ads)
            print(f"✅ Найдено {new_count} новых объявлений. Обновлён seen_ads.json.")
        else:
            print("ℹ️ Новых объявлений нет.")

    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
