from playwright.sync_api import sync_playwright
import requests
import os
import json
from urllib.parse import urljoin

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/mini+gt+/mini-gt/MTY9"
SEEN_FILE = "seen.json"


# ---------------- LOAD SEEN ----------------
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
def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


# ---------------- PRODUCT FILTER (IMPORTANT FIX) ----------------
def is_real_product(href):
    if not href:
        return False

    href = href.lower()

    # must be product detail page
    if "/details/" not in href:
        return False

    # remove category pages (too shallow)
    parts = href.strip("/").split("/")
    if len(parts) <= 4:
        return False

    # block pure category pages
    if href.endswith("mini-gt/"):
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
        page.wait_for_timeout(5000)

        # 🔥 ONLY target links that look like products
        links = page.locator("a[href*='/details/']").all()

        print("Links found:", len(links))

        for a in links:
            try:
                text = a.inner_text().strip()
                href = a.get_attribute("href")

                href = urljoin(URL, href)

                # 🚨 STRICT FILTER
                if not is_real_product(href):
                    continue

                current.add(href)

                print("PRODUCT:", text)
                print("LINK:", href)

                # 🔥 ALERT ONLY NEW ITEMS
                if href not in seen:
                    send_telegram(f"""🔥 MINI GT RESTOCK ALERT

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
