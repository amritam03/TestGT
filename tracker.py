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

print("Checking Mini GT page...")

r = requests.get(URL, headers=headers)

print("Website:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

current = set()

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)
    href = a["href"]

    if "MINI GT" not in text.upper():
        continue

    if "/details/" not in href:
        continue

    if href.startswith("/"):
        link = "https://www.karzanddolls.com" + href
    else:
        link = href

    product_id = link
    current.add(product_id)

    if product_id not in seen:

        msg = f"""
🔥 NEW / RESTOCKED MINI GT

🚗 {text}

🛒 Buy:
{link}
"""

        send(msg)

seen = current

with open(SEEN_FILE, "w") as f:
    json.dump(list(seen), f)

print("Saved", len(seen), "products")
