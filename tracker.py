import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent":"Mozilla/5.0"
}

def send_photo(img, caption):

    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "caption": caption
        },
        files={}
        if not img else None,
        json=None if img else {},
        params=None,
    ) if not img else requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "photo": img,
            "caption": caption
        }
    )

    print("Telegram:", r.status_code)
    print(r.text)

print("Loading page...")

r = requests.get(URL, headers=headers)

print("Website:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a")

sent = 0

for a in links:

    title = a.get_text(" ", strip=True)
    href = a.get("href")

    if "MINI GT" not in title.upper():
        continue

    if not href:
        continue

    if href.startswith("/"):
        link = "https://www.karzanddolls.com" + href
    else:
        link = href

    print("Opening:", link)

    try:
        p = requests.get(link, headers=headers, timeout=15)

        psoup = BeautifulSoup(p.text, "html.parser")

        price = "Price unavailable"

        for t in psoup.stripped_strings:
            if "₹" in t:
                price = t
                break

        img = ""

        tag = psoup.find("img")

        if tag:
            img = tag.get("src","")

        caption = f"""🚗 {title}

💰 {price}

🛒 Buy:
{link}
"""

        send_photo(img, caption)

        sent += 1

        break

    except Exception as e:
        print(e)

print("Sent:", sent)
