import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent":"Mozilla/5.0"
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

print("Loading Mini GT page...")

r = requests.get(URL, headers=headers)

print("Website:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

sent = 0

# Find only links that look like product detail pages
for a in soup.find_all("a", href=True):

    href = a["href"]
    text = a.get_text(" ", strip=True)

    # Skip empty titles
    if len(text) < 10:
        continue

    # Product pages usually contain /details/
    if "/details/" not in href:
        continue

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

    break

print("Sent:", sent)
