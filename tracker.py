import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent":"Mozilla/5.0"
}

def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    print("Telegram:", r.status_code)
    print(r.text)

print("Checking...")

r = requests.get(URL, headers=headers)

print("Website:", r.status_code)

soup = BeautifulSoup(r.text,"html.parser")

links = soup.find_all("a")

count = 0

for a in links:

    text = a.get_text(" ",strip=True)
    href = a.get("href")

    if "MINI GT" in text.upper():

        print("FOUND:", text)

        msg = f"""
🚗 {text}

Buy:
https://www.karzanddolls.com{href}
"""

        send(msg)

        count += 1

        break

print("Sent:", count)
