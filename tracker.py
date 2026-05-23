import requests
from bs4 import BeautifulSoup
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE = "https://www.karzanddolls.com"

# Actual Mini GT listings page
URL = "https://www.karzanddolls.com/details/mini+gt+/mini-gt/584a9174094561d2887298e8db583ec307aac8568640e1a6630e7383bb3f8817d39cc8ba615fa8fd330999d32c2677354350185ca7c076241f55f8892db3776a4CArOJdO0gY2NwetVohbP2EiwFNxqmYO06v_G1InTW0-"

headers = {
    "User-Agent":"Mozilla/5.0"
}

SEEN_FILE="seen.json"

try:
    with open(SEEN_FILE,"r") as f:
        seen=set(json.load(f))
except:
    seen=set()

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id":CHAT_ID,
            "text":msg
        }
    )

print("Opening Mini GT listings...")

r=requests.get(URL,headers=headers)

print("Status:",r.status_code)

soup=BeautifulSoup(
    r.text,
    "html.parser"
)

current=set()

links=soup.find_all("a",href=True)

print("Links:",len(links))

for a in links:

    text=a.get_text(
        " ",
        strip=True
    )

    href=a["href"]

    # real products usually have long names
    if len(text)<20:
        continue

    if href.startswith("/"):
        link=BASE+href
    else:
        link=href

    # avoid category pages
    if "/details/" not in link:
        continue

    if "mini+gt" not in link.lower():
        continue

    if link in current:
        continue

    current.add(link)

    print("PRODUCT:",text)
    print("LINK:",link)

    if link not in seen:

        msg=f"""🔥 MINI GT RESTOCK

🚗 {text}

🛒 Buy:
{link}
"""

        send(msg)

with open(
    SEEN_FILE,
    "w"
) as f:

    json.dump(
        list(current),
        f
    )

print("Saved:",len(current))
