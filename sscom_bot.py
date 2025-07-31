import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from telegram import Bot

SEEN_FILE = "seen_ads.json"
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def load_seen_ads():
    if not os.path.exists(SEEN_FILE):
        print(f"⚠️ Файл {SEEN_FILE} не найден. Создаём пустой []")
        return []
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"📂 Загружено {len(data)} хэшей из {SEEN_FILE}")
            return data
    except Exception as e:
        print(f"❌ Ошибка чтения {SEEN_FILE}: {e}")
        return []


def save_seen_ads(seen_ads):
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_ads, f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(seen_ads)} хэшей в {SEEN_FILE}")
    except Exception as e:
        print(f"❌ Ошибка записи {SEEN_FILE}: {e}")


def fetch_ads():
    print(f"🌐 Загружаем страницу: {URL}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"❌ Ошибка загрузки страницы: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    ads = []
    rows = soup.select("tr[id^='tr_'] td.msga2 > a")

    for link in rows:
        title = link.get_text(strip=True)
        href = link.get("href")
        if href and not href.startswith("http"):
            href = "https://www.ss.com" + href
        ads.append((title, href))

    print(f"🔍 Найдено {len(ads)} объявлений (всего на странице).")
    return ads


def is_119_series(link):
    try:
        print(f"🔎 Проверяем: {link}")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Не удалось загрузить: {link}")
            return False
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text().lower()

        keywords = [
            "119 серия", "119. серия", "119-я серия", "119я серия",
            "серия 119", "серия 119-я", "серии 119", "119-я", "119я"
        ]

        if any(keyword in content for keyword in keywords):
            print("✅ Найдена 119 серия")
            return True
        else:
            print("⏩ Пропущено (не 119 серия):", link)
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке 119 серии: {e}")
        return False


def send_to_telegram(messages):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_TOKEN или CHAT_ID не заданы!")
        return
    bot = Bot(token=TELEGRAM_TOKEN)
    for msg in messages:
        try:
            bot.send_message(chat_id=CHAT_ID, text=msg)
            print(f"📬 Отправлено: {msg[:50]}...")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")


def main():
    print("▶️ Бот запущен. Проверка объявлений...")
    seen_ads = load_seen_ads()
    ads = fetch_ads()

    new_ads = []
    for title, link in ads:
        hash_id = hashlib.sha256((title + link).encode("utf-8")).hexdigest()
        if hash_id in seen_ads:
            continue
        if not is_119_series(link):
            continue
        new_ads.append((title, link))
        seen_ads.append(hash_id)

    print(f"🆕 Найдено {len(new_ads)} новых объявлений (фильтр: 119).")
    if new_ads:
        messages = [f"{title}\n{link}" for title, link in new_ads]
        send_to_telegram(messages)
        save_seen_ads(seen_ads)
    else:
        print("ℹ️ Новых подходящих объявлений нет.")


if __name__ == "__main__":
    main()
