import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("8983135704:AAEPecaHWbRY7Rej3fKaC2_JeeKYZPAzQHw")
CHAT_ID = os.getenv("982948994")

URL = "https://www.karzanddolls.com/search?search=mini%20gt"

def send(msg):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )
    print("Telegram:", r.status_code)

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Checking website...")

r = requests.get(URL, headers=headers)

print("Website status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

found = False

for text in soup.stripped_strings:

    if "MINI GT" in text.upper():

        found = True
        print("Found:", text)

        send(f"🔥 Mini GT detected:\n\n{text}")

        break

if not found:
    print("No Mini GT found")
