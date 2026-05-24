import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Main Mini GT Collection Catalog URL
TARGET_URL = "https://www.karzanddolls.com/details/tsm+model+cars/mini-gt/MTY1"

def check_restock():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Missing Telegram Environment Secrets.")
        sys.exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Server returned status code: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # KarzAndDolls groups catalog entries within dedicated wrapper grid columns
        product_cards = soup.find_all("div", class_=lambda c: c and ("col-" in c or "product" in c.lower()))
        
        print("Scan running. Analyzing catalog items...")
        processed_count = 0

        for card in product_cards:
            # 1. Price Tag Extraction (Crucial filter to ensure it's a real product card)
            price_elem = card.find(string=lambda text: text and any(marker in text for marker in ["Rs.", "₹"]))
            if not price_elem:
                continue
            price = price_elem.strip()
            
            # 2. Extract Product Image URL
            img_elem = card.find("img")
            img_url = None
            if img_elem:
                img_src = img_elem.get("data-src") or img_elem.get("src")
                if img_src:
                    img_url = urljoin("https://www.karzanddolls.com", img_src)

            # 3. FIX: Safely extract the deep, complex KarzAndDolls dynamic buy links
            product_url = None
            
            # Find all absolute links within this specific model card
            anchors = card.find_all("a", href=True)
            for a in anchors:
                href = a["href"]
                # The correct buy links on their platform explicitly contain "/product/" inside the path string
                if "/product/" in href.lower():
                    product_url = urljoin("https://www.karzanddolls.com", href)
                    break # Success! We found the real checkout link. Stop searching this card.

            # If no link contains "/product/", pull the parent anchor wrapping the model image thumbnail
            if not product_url and img_elem:
                parent_a = img_elem.find_parent("a", href=True)
                if parent_a:
                    product_url = urljoin("https://www.karzanddolls.com", parent_a["href"])

            # If it still can't find a direct link, skip this specific element to prevent bad pings
            if not product_url or product_url == "https://www.karzanddolls.com" or "javascript" in product_url.lower():
                continue

            # 4. Extract Model Name/Title
            title = None
            for a in anchors:
                text = a.get_text(strip=True)
                if "MINI GT" in text.upper() and len(text) > 10 and "SELECT A SIZE" not in text.upper():
                    title = text
                    break
            
            # Fallback for Title naming matching
            if not title and img_elem and img_elem.get("alt"):
                title = img_elem["alt"].strip()
            if not title:
                title = "Mini GT Scaled Model"

            # Format beautiful notification presentation layout for Telegram
            caption = (
                f"🚨 *NEW MINI GT STOCK DETECTED!* 🚨\n\n"
                f"🚘 *Model:* {title}\n"
                f"💰 *Price:* {price}\n\n"
                f"🔗 *Buy Now:* {product_url}"
            )
            
            send_telegram_photo_alert(img_url, caption)
            processed_count += 1
            
        print(f"Successfully tracked and delivered {processed_count} active Mini GT model notifications.")
            
    except Exception as e:
        print(f"An error occurred inside the execution pipeline: {e}")

def send_telegram_photo_alert(image_url, caption_text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption_text,
        "parse_mode": "Markdown"
    }
    
    if image_url:
        payload["photo"] = image_url
    else:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload["text"] = caption_text
        del payload["caption"]

    try:
        res = requests.post(telegram_url, json=payload, timeout=12)
        if res.status_code != 200:
            print(f"Telegram API Warning: Response code {res.status_code}")
    except Exception as e:
        print(f"Failed photo upload routing to target channel device: {e}")

if __name__ == "__main__":
    check_restock()
