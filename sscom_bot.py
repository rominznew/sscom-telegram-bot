import requests
from bs4 import BeautifulSoup
import json
import os
import hashlib
import time

URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen_ads.json")


def load_seen_ads():
    """Загружаем список уже отправленных объявлений"""
    if not os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            f.write("[]")
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        print(f"❌ Ошибка чтения seen_ads.json: {e}")
        return set()


def save_seen_ads(seen_ads):
    """Сохраняем хэши объявлений"""
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_ads), f, indent=2, ensure_ascii=False)
        print(f"💾 Сохранено {len(seen_ads)} хэшей в seen_ads.json")
    except Exception as e:
        print(f"❌ Ошибка записи seen_ads.json: {e}")


def get_ads():
    """Парсим объявления с SS.com"""
    print(f"🌐 Загружаем страницу: {URL}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"❌ Ошибка загрузки страницы: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr[id^='tr_']")
    print(f"🔍 Найдено {len(rows)} объявлений (всего на странице).")

    ads = []
    for row in rows:
        title_tag = row.select_one("a.am")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = "https://www.ss.com" + title_tag["href"]
        ad_hash = hashlib.md5(link.encode()).hexdigest()
        ads.append((ad_hash, f"{title}\n{link}"))
    return ads


def send_telegram_message(message):
    """Отправляем сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print(f"⚠️ Ошибка отправки: {r.text}")
        else:
            print(f"📬 Отправлено: {message[:60]}")
    except Exception as e:
        print(f"❌ Ошибка Telegram API: {e}")


def main():
    print("▶️ Бот запущен. Проверка объявлений...")
    seen_ads = load_seen_ads()
    ads = get_ads()
    new_ads = []

    for ad_hash, ad_text in ads:
        if ad_hash not in seen_ads:
            new_ads.append((ad_hash, ad_text))
            send_telegram_message(ad_text)
            seen_ads.add(ad_hash)
            time.sleep(1)

    if new_ads:
        print(f"🆕 Найдено {len(new_ads)} новых объявлений.")
    else:
        print("ℹ️ Новых объявлений нет.")

    save_seen_ads(seen_ads)


if __name__ == "__main__":
    main()
