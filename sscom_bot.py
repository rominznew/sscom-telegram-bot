import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot

# Настройки
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"
SEEN_FILE = "seen_ads.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)


def load_seen_ads():
    """Загрузка списка просмотренных объявлений"""
    if not os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        print(f"⚠ Ошибка чтения {SEEN_FILE}: {e}")
        return set()


def save_seen_ads(seen_ads):
    """Сохранение списка просмотренных объявлений"""
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_ads), f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(seen_ads)} хэшей в {SEEN_FILE}")
    except Exception as e:
        print(f"⚠ Ошибка сохранения {SEEN_FILE}: {e}")


def get_ads():
    """Парсинг страницы объявлений"""
    print(f"🌐 Загружаем страницу: {URL}")
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    ads = []
    table = soup.find("table", {"id": "filter_tbl"})
    if not table:
        print("⚠ Не удалось найти таблицу с объявлениями.")
        return ads

    for row in table.find_all("tr", {"id": lambda x: x and x.startswith("tr_")}):
        title_cell = row.find("a", {"class": "am"})
        if title_cell:
            title = title_cell.get_text(strip=True)
            link = "https://www.ss.com" + title_cell.get("href")
            ads.append({"title": title, "link": link})

    print(f"🔍 Найдено {len(ads)} объявлений (всего на странице).")
    return ads


def send_new_ads():
    seen_ads = load_seen_ads()
    current_ads = get_ads()

    new_ads = []
    for ad in current_ads:
        ad_hash = hashlib.md5(ad["link"].encode()).hexdigest()
        if ad_hash not in seen_ads:
            new_ads.append(ad)
            seen_ads.add(ad_hash)

    print(f"🆕 Найдено {len(new_ads)} новых объявлений.")

    if new_ads:
        for ad in new_ads:
            message = f"{ad['title']}\n{ad['link']}"
            try:
                bot.send_message(chat_id=CHAT_ID, text=message)
                print(f"📬 Отправлено: {ad['title']}")
            except Exception as e:
                print(f"⚠ Ошибка отправки: {e}")
        save_seen_ads(seen_ads)
    else:
        print("ℹ️ Новых объявлений нет.")


if __name__ == "__main__":
    print("▶️ Бот запущен. Проверка объявлений...")
    send_new_ads()
