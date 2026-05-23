import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE = "https://www.karzanddolls.com"
URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}

SEEN_FILE = "seen.json"

try:
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()


def send(msg):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )
    print("Telegram:", r.status_code)


print("Opening Mini GT page...")

r = requests.get(URL, headers=headers, timeout=30)
print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

current = set()

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)
    href = a["href"]

    if len(text) < 8:
        continue

    link = urljoin(BASE, href)

    # Skip category page itself
    if link == URL:
        continue

    # Skip already checked duplicates
    if link in current:
        continue

    try:
        # Open candidate page
        p = requests.get(link, headers=headers, timeout=15)

        if p.status_code != 200:
            continue

        psoup = BeautifulSoup(p.text, "html.parser")

        page_text = psoup.get_text(" ", strip=True).upper()

        # Verify this is a real Mini GT product page
        if "MINI GT" not in page_text:
            continue

        # Try to find title
        title = ""

        if psoup.title:
            title = psoup.title.text.strip()

        if len(title) < 5:
            title = text

        current.add(link)

        print("PRODUCT:", title)
        print("LINK:", link)

        if link not in seen:

            msg = f"""🔥 MINI GT RESTOCK

🚗 {title}

🛒 Buy:
{link}
"""

            send(msg)

    except Exception as e:
        print("ERROR:", e)

with open(SEEN_FILE, "w") as f:
    json.dump(list(current), f)

print("Saved:", len(current))
