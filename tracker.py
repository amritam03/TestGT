import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send(msg):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

    print("Telegram:", r.status_code)
    print(r.text)

print("Loading Mini GT page...")

r = requests.get(URL, headers=headers)

print("Website:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

sent = 0

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)
    href = a["href"]

    # Must contain MINI GT
    if "MINI GT" not in text.upper():
        continue

    # Must be an individual product page
    if "/details/" not in href:
        continue

    # Build full link
    if href.startswith("/"):
        link = "https://www.karzanddolls.com" + href
    else:
        link = href

    msg = f"""
🚗 {text}

🛒 Buy:
{link}
"""

    print(msg)

    send(msg)

    sent += 1

    # Send only first result while testing
    break

print("Sent:", sent)
