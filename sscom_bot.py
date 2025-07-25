import requests
from bs4 import BeautifulSoup
import json
import os
import hashlib
from telegram import Bot

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://www.ss.com/ru/real-estate/flats/riga/ziepniekkalns/"

SEEN_FILE = "seen_ads.json"

# === ФУНКЦИИ ===
def load_seen_ads():
    if not os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            f.write("[]")
        return []
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_seen_ads(seen_ads):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_ads, f, ensure_ascii=False, indent=2)
    print(f"💾 Сохранено {len(seen_ads)} хэшей в {SEEN_FILE}")

def get_ads():
    print(f"🌐 Загружаем страницу: {URL}")
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    
    ads = []
    for row in soup.select("tr[id^='tr_']"):
        title_tag = row.select_one("td.msg2 a")
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = "https://www.ss.com" + title_tag.get("href")
            ad_hash = hashlib.md5(link.encode()).hexdigest()
            ads.append({"title": title, "link": link, "hash": ad_hash})
    print(f"🔍 Найдено {len(ads)} объявлений (всего на странице).")
    return ads

def send_to_telegram(bot, message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print(f"📬 Отправлено: {message[:60]}")

def main():
    print("▶️ Бот запущен. Проверка объявлений...")
    bot = Bot(token=TELEGRAM_TOKEN)

    seen_ads = load_seen_ads()
    ads = get_ads()

    new_ads = [ad for ad in ads if ad["hash"] not in seen_ads]
    print(f"🆕 Найдено {len(new_ads)} новых объявлений.")

    if new_ads:
        for ad in new_ads:
            send_to_telegram(bot, ad["title"] + "\n" + ad["link"])
            seen_ads.append(ad["hash"])
        save_seen_ads(seen_ads)
    else:
        print("ℹ️ Новых объявлений нет.")

if __name__ == "__main__":
    main()
