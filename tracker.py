from playwright.sync_api import sync_playwright
import requests
import os
import json
from urllib.parse import urljoin

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/mini+gt+/mini-gt/MTY5"
SEEN_FILE = "seen.json"


# ---------------- LOAD STATE ----------------
def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


seen = load_seen()


# ---------------- TELEGRAM ----------------
def send(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing Telegram env vars")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


# ---------------- FILTER ----------------
def is_product(href):
    if not href:
        return False

    href = href.lower()

    # must be product page
    if "/details/" not in href:
        return False

    # remove category pages
    if href.count("/") <= 4:
        return False

    return True


# ---------------- SCRAPER ----------------
def scrape():
    current = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Opening page...")
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        links = page.locator("a[href*='/details/']").all()

        print("Links found:", len(links))

        for a in links:
            try:
                text = a.inner_text().strip()
                href = a.get_attribute("href")

                href = urljoin(URL, href)

                if not is_product(href):
                    continue

                current.add(href)

                print("FOUND:", text)
                print("LINK:", href)

                # NEW PRODUCT ALERT
                if href not in seen:
                    send(f"""🔥 MINI GT RESTOCK ALERT

🚗 {text}

🛒 Buy Now:
{href}
""")

                    seen.add(href)

            except Exception as e:
                print("Error:", e)

        browser.close()

    return current


# ---------------- MAIN ----------------
if __name__ == "__main__":
    scrape()
    save_seen(seen)
