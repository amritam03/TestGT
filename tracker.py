import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TARGET_URL = "https://www.karzanddolls.com/details/tsm+model+cars/mini-gt/MTY1"
HISTORY_FILE = "inventory.txt"

known_products = set()
is_first_run_ever = False

# Read saved data
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        known_products = set(line.strip() for line in f if line.strip())
    print(f"Loaded {len(known_products)} baseline products from tracking storage.")
else:
    print("No previous tracking file found. Building a quiet baseline map right now.")
    is_first_run_ever = True

def fetch_and_check():
    global known_products, is_first_run_ever
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[{time.strftime('%H:%M:%S')}] Server returned status: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, "html.parser")
        product_cards = soup.find_all("div", class_=lambda c: c and ("col-" in c or "product" in c.lower()))
        
        current_scan_links = set()
        new_items_alerted = 0
        
        for card in product_cards:
            price_elem = card.find(string=lambda text: text and any(marker in text for marker in ["Rs.", "₹"]))
            if not price_elem:
                continue
            price = price_elem.strip()
            
            img_elem = card.find("img")
            img_url = None
            if img_elem:
                img_src = img_elem.get("data-src") or img_elem.get("src")
                if img_src:
                    img_url = urljoin("https://www.karzanddolls.com", img_src)

            product_url = None
            anchors = card.find_all("a", href=True)
            for a in anchors:
                href = a["href"]
                if "/product/" in href.lower():
                    product_url = urljoin("https://www.karzanddolls.com", href)
                    break 

            if not product_url or product_url == "https://www.karzanddolls.com" or "javascript" in product_url.lower():
                continue

            current_scan_links.add(product_url)

            # Quiet Setup: Populates baseline memory list on initial execution
            if is_first_run_ever:
                known_products.add(product_url)
                continue

            # Filtering out known inventory entries
            if product_url in known_products:
                continue

            # Process new listing alerts
            title = None
            for a in anchors:
                text = a.get_text(strip=True)
                if "MINI GT" in text.upper() and len(text) > 10 and "SELECT A SIZE" not in text.upper():
                    title = text
                    break
            
            if not title and img_elem and img_elem.get("alt"):
                title = img_elem["alt"].strip()
            if not title:
                title = "Mini GT Scaled Model"

            caption = (
                f"🚨 *NEW MINI GT ARRIVAL / RESTOCK!* 🚨\n\n"
                f"🚘 *Model:* {title}\n"
                f"💰 *Price:* {price}\n\n"
                f"🔗 *Buy Now:* {product_url}"
            )
            
            send_telegram_photo_alert(img_url, caption)
            known_products.add(product_url)
            new_items_alerted += 1
            
        print(f"[{time.strftime('%H:%M:%S')}] Check complete. Found {new_items_alerted} restocks.")
        
        with open(HISTORY_FILE, "w") as f:
            for link in current_scan_links:
                f.write(f"{link}\n")
                
        if is_first_run_ever:
            is_first_run_ever = False
            print("Initial tracking template built. Real-time alert listeners are active!")
                
    except Exception as e:
        print(f"Error inside processing engine loop: {e}")

def send_telegram_photo_alert(image_url, caption_text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption_text, "parse_mode": "Markdown"}
    if image_url:
        payload["photo"] = image_url
    else:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload["text"] = caption_text
        del payload["caption"]
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed Telegram delivery: {e}")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing credentials. Halting tracker.")
        sys.exit(1)

    for i in range(5):
        print(f"Running check cycle {i+1} of 5...")
        fetch_and_check()
        if i < 4:
            time.sleep(60)
