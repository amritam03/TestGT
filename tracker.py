import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TARGET_URL = "https://www.karzanddolls.com/details/tsm+model+cars/mini-gt/MTY1"

# Memory bank to store products we have already alerted you about during this run
sent_notifications = set()

def fetch_and_check():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[{time.strftime('%H:%M:%S')}] Server returned error status: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, "html.parser")
        product_cards = soup.find_all("div", class_=lambda c: c and ("col-" in c or "product" in c.lower()))
        
        new_items_found = 0
        
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

            # FIX: Use the unique product URL as a fingerprint to prevent duplicates
            if product_url in sent_notifications:
                continue # We already sent this one, skip it!

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
                f"🚨 *NEW MINI GT STOCK DETECTED!* 🚨\n\n"
                f"🚘 *Model:* {title}\n"
                f"💰 *Price:* {price}\n\n"
                f"🔗 *Buy Now:* {product_url}"
            )
            
            send_telegram_photo_alert(img_url, caption)
            
            # Add this item to memory so we don't alert you again on the next 1-minute loop
            sent_notifications.add(product_url)
            new_items_found += 1
            
        print(f"[{time.strftime('%H:%M:%S')}] Check done. Sent {new_items_found} new alerts.")
            
    except Exception as e:
        print(f"Error encountered during active scan loop: {e}")

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
        print(f"Failed alert delivery: {e}")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Missing Telegram Credentials.")
        sys.exit(1)

    print("Starting smart 1-minute loop sequence...")
    
    # Run the loop sequence
    for i in range(5):
        print(f"Running check cycle {i+1} of 5...")
        fetch_and_check()
        
        if i < 4:
            time.sleep(60)
            
    print("Loop sequence completed successfully.")
