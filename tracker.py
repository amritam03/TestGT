import requests
from bs4 import BeautifulSoup
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

SEEN_FILE = "seen.json"

try:
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

print("Loading Mini GT page...")

r = requests.get(URL, headers=headers)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

current = set()

cards = soup.select("div.productbox")

print("Products found:", len(cards))

for card in cards:

    try:

        title_tag = card.select_one("a")

        if not title_tag:
            continue

        title = title_tag.get_text(
            " ",
            strip=True
        )

        href = title_tag.get(
            "href"
        )

        if not href:
            continue

        if href.startswith("/"):
            link = (
                "https://www.karzanddolls.com"
                + href
            )
        else:
            link = href

        price = "Unknown"

        price_tag = card.find(
            text=lambda t:
            t and "₹" in t
        )

        if price_tag:
            price = price_tag.strip()

        print("TITLE:", title)
        print("LINK:", link)

        current.add(link)

        if link not in seen:

            msg=f"""
🔥 MINI GT RESTOCK

🚗 {title}

💰 {price}

🛒 Buy:
{link}
"""

            send(msg)

    except Exception as e:
        print(e)

with open(
    SEEN_FILE,
    "w"
) as f:

    json.dump(
        list(current),
        f
    )

print("Saved:",len(current))
