import requests
from bs4 import BeautifulSoup
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

SEEN_FILE = "seen.json"

try:
    with open(SEEN_FILE,"r") as f:
        seen = set(json.load(f))
except:
    seen = set()

headers = {
    "User-Agent":"Mozilla/5.0"
}

def send_product(name, price, link, image):

    caption = f"""
🚗 *Mini GT Restock Alert*

*{name}*

💰 Price: {price}

🛒 Buy:
{link}
"""

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "photo": image,
            "caption": caption,
            "parse_mode": "Markdown"
        }
    )

print("Checking Mini GT page...")

r = requests.get(URL, headers=headers)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text,"html.parser")

products = soup.find_all("a")

count=0

for p in products:

    text = p.get_text(" ",strip=True)

    href = p.get("href")

    if "MINI GT" not in text.upper():
        continue

    if text in seen:
        continue

    seen.add(text)

    link = (
        "https://www.karzanddolls.com"+href
        if href and href.startswith("/")
        else URL
    )

    # visit product page
    try:

        page=requests.get(
            link,
            headers=headers
        )

        psoup=BeautifulSoup(
            page.text,
            "html.parser"
        )

        img=""

        image_tag=psoup.find("img")

        if image_tag:
            img=image_tag.get("src","")

        price="Not found"

        for t in psoup.stripped_strings:
            if "₹" in t:
                price=t
                break

        send_product(
            text,
            price,
            link,
            img
        )

        count +=1

    except Exception as e:
        print(e)

with open(
    SEEN_FILE,
    "w"
) as f:

    json.dump(
        list(seen),
        f
    )

print("Sent:",count)
