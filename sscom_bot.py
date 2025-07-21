import requests
from bs4 import BeautifulSoup
import os
import json
import hashlib

URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
SEEN_FILE = "seen_ads.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ================== Вспомогательные функции ==================

def load_seen_ads():
    """Загружаем список ранее найденных объявлений"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_seen_ads(seen_ads):
    """Сохраняем список объявлений"""
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ads), f, ensure_ascii=False, indent=2)

def get_ad_hash(title, url):
    """Создаём уникальный хэш объявления по заголовку и ссылке"""
    return hashlib.md5(f"{title}{url}".encode("utf-8")).hexdigest()

def send_telegram_message(message):
    """Отправляем сообщение в Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_TOKEN или CHAT_ID не заданы!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"⚠️ Ошибка отправки сообщения в Telegram: {response.status_code} {response.text}")
        else:
            print(f"📩 Уведомление отправлено: {message}")
    except Exception as e:
        print(f"⚠️ Ошибка при запросе к Telegram API: {e}")

# ================== Основная логика ==================

def get_latest_ads():
    """Парсим страницу SS.com и ищем новые объявления"""
    print(f"🌐 Загружаем страницу: {URL}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Новый селектор для ссылок на объявления
    ads = soup.select('a.am')
    print(f"🔍 Найдено {len(ads)} объявлений на странице.")

    new_ads = []
    for link_tag in ads:
        title = link_tag.text.strip()
        relative_url = link_tag['href']
        if not relative_url.startswith('http'):
            full_url = 'https://www.ss.com' + relative_url
        else:
            full_url = relative_url

        ad_hash = get_ad_hash(title, full_url)
        if ad_hash not in seen_ads:
            seen_ads.add(ad_hash)
            new_ads.append((title, full_url))

    return new_ads

# ================== Запуск ==================

if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")

    seen_ads = load_seen_ads()

    try:
        new_ads = get_latest_ads()
        if new_ads:
            print(f"✨ Найдено {len(new_ads)} новых объявлений.")
            for title, url in new_ads:
                msg = f"🏠 Новое объявление:\n{title}\n{url}"
                send_telegram_message(msg)
        else:
            print("ℹ️ Новых объявлений нет.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    save_seen_ads(seen_ads)
    print(f"💾 Сохранено {len(seen_ads)} объявлений в {SEEN_FILE}")
