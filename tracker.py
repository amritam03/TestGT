import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.getenv("8983135704:AAEPecaHWbRY7Rej3fKaC2_JeeKYZPAzQHw")
CHAT_ID = os.getenv("982948994")

URL="https://www.karzanddolls.com/search?search=mini%20gt"

seen=set()

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id":CHAT_ID,
            "text":msg
        }
    )

def check_stock():

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

            if text not in seen:

                seen.add(text)

                if href:

                    send(
f"🔥 Mini GT found!\n\n{text}\nhttps://www.karzanddolls.com{href}"
                    )

while True:

    try:
        check_stock()

    except Exception as e:
        print(e)

    time.sleep(30)
