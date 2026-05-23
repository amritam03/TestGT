from playwright.sync_api import sync_playwright
import requests
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/mini+gt+/mini-gt/MTY1"

SEEN_FILE = "seen.json"

try:
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


current = set()

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("Opening page...")
    page.goto(URL, wait_until="networkidle")

    page.wait_for_timeout(5000)

    links = page.locator("a").all()

    print("Total:", len(links))

    for a in links:

        try:
            text = a.inner_text().strip()
            href = a.get_attribute("href")

            if not text:
                continue

            # real Mini GT products usually have model names
            if "MINI GT" not in text.upper():
                continue

            if len(text) < 15:
                continue

            if not href:
                continue

            if href.startswith("/"):
                href = "https://www.karzanddolls.com" + href

            current.add(href)

            print("PRODUCT:", text)
            print("LINK:", href)

            if href not in seen:

                msg = f"""🔥 MINI GT RESTOCK

🚗 {text}

🛒 Buy:
{href}
"""

                send(msg)

        except:
            pass

    browser.close()


with open(SEEN_FILE, "w") as f:
    json.dump(list(current), f)

print("Saved:", len(current))
