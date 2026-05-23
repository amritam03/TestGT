import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Checking Mini GT page...")

r = requests.get(URL, headers=headers)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

items = []

for text in soup.stripped_strings:
    t = text.strip()

    if "MINI GT" in t.upper() and len(t) > 15:
        if t not in items:
            items.append(t)

print("Found:", len(items))

for item in items[:5]:
    print(item)
    send(f"🚗 Mini GT found:\n\n{item}")

print("Done")
