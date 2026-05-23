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
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )
    print("Telegram:", r.status_code)

print("Loading Mini GT page...")

r = requests.get(URL, headers=headers)
print("Website:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

current = set()

for a in soup.find_all("a", href=True):

    href = a["href"]
    text = a.get_text(" ", strip=True)

    # skip empty names
    if len(text) < 10:
        continue

    # must be Mini GT
    if "MINI GT" not in text.upper():
        continue

    # ignore category page itself
    if href.endswith("/MTY1"):
        continue

    # only actual product pages
    if "/details/" not in href:
        continue

    if href.startswith("/"):
        link = "https://www.karzanddolls.com" + href
    else:
        link = href

    # prevent duplicates
    if link in current:
        continue

    current.add(link)

    print("PRODUCT:", text)
    print("LINK:", link)

    if link not in seen:

        msg = f"""🔥 MINI GT RESTOCK

🚗 {text}

🛒 Buy:
{link}
"""

        send(msg)

with open(SEEN_FILE, "w") as f:
    json.dump(list(current), f)

print("Saved:", len(current))
