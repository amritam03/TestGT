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

# Load previously known items from the saved history file
known_products = set()
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        known_products = set(line.strip() for line in f if line.strip())
    print(f"Loaded {len(known_products)} baseline products from persistent storage.")
else:
    print("No previous inventory file found. This might be the first setup run.")

def fetch_and_check():
    global known_products
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[{time.strftime('%H:%M:%S')}] Server error: {response.status_code}")
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

            # Keep a record of everything currently live on the site
            current_scan_links.add(product_url)

            # CRITICAL FILTER: If we already know this product, skip it entirely!
            if product_url in known_products:
                continue

            # If we reach here, it's a genuine new listing or a fresh restock!
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
            
            # Immediately add to our local set so we don't alert again in the next 1-minute loop iteration
            known_products.add(product_url)
            new_items_alerted += 1
            
        print(f"[{time.strftime('%H:%M:%S')}] Check complete. Dispatched {new_items_alerted} new restock alerts.")
        
        # Save our updated list back to the text file
        with open(HISTORY_FILE, "w") as f:
            for link in current_scan_links:
                f.write(f"{link}\n")
                
    except Exception as e:
        print(f"Error during execution scan: {e}")

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
        print(f"Failed to drop Telegram ping: {e}")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing variables. Halting pipeline.")
        sys.exit(1)

    # 5 iterations spaced 1 minute apart = 5 total minutes
    for i in range(5):
        print(f"Running check cycle {i+1} of 5...")
        fetch_and_check()
        if i < 4:
            time.sleep(60)
