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

print("Checking Mini GT page...")

r = requests.get(URL, headers=headers)

print("Website:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

for a in soup.find_all("a"):

    text = a.get_text(" ", strip=True)
    href = a.get("href")

    if "MINI GT" in text.upper():

        link = ""

        if href:
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

        break
