import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/search?q=mini+gt"

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

print("Checking Mini GT listings...")

r = requests.get(URL, headers=headers)

print("Website status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

found = []

for text in soup.stripped_strings:
    if "MINI GT" in text.upper():
        if text not in found:
            found.append(text)

for item in found[:5]:
    send(f"🚗 Mini GT found:\n\n{item}")

print("Done")
