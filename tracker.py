import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")

URL="https://www.karzanddolls.com/search?search=mini%20gt"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id":CHAT_ID,
            "text":msg
        }
    )

headers={
    "User-Agent":"Mozilla/5.0"
}

r=requests.get(URL,headers=headers)

soup=BeautifulSoup(
    r.text,
    "html.parser"
)

for a in soup.find_all("a"):

    text=a.get_text(strip=True)

    href=a.get("href")

    if "MINI GT" in text.upper():

        if href:

            send(
f"🔥 Mini GT listing found\nhttps://www.karzanddolls.com{href}"
            )

            break
