import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Main Mini GT Catalog Page URL
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
        
        # KarzAndDolls structures individual item grids inside card elements or item wrappers.
        # We will parse out all structural product nodes to isolate individual details cleanly.
        product_cards = soup.select(".product-box") or soup.select("[class*='col-']") or soup.find_all("div", class_=lambda c: c and "product" in c.lower())
        
        print(f"Scan running. Found {len(product_cards)} grid container elements.")
        
        processed_count = 0

        for card in product_cards:
            # Check for pricing to guarantee it's a valid, active store option
            price_elem = card.find(string=lambda text: text and any(marker in text for marker in ["Rs.", "₹"]))
            if not price_elem:
                continue
                
            price = price_elem.strip()
            
            # Extract the specific product listing page URL anchor
            link_elem = card.find("a", href=True)
            if not link_elem:
                continue
            product_url = urljoin("https://www.karzanddolls.com", link_elem["href"])
            
            # Extract Image URL string element
            img_elem = card.find("img")
            img_url = None
            if img_elem:
                # Fallback structure handles common lazy-loading image attributes on e-commerce platforms
                img_src = img_elem.get("data-src") or img_elem.get("src")
                if img_src:
                    img_url = urljoin("https://www.karzanddolls.com", img_src)
            
            # Isolate the exact item title variant text
            # Cleans common boilerplate out to maximize title accuracy 
            title = "Unknown Mini GT Model"
            title_candidates = card.find_all(["h4", "h5", "p", "a"])
            for candidate in title_candidates:
                text = candidate.get_text(strip=True)
                if "MINI GT" in text.upper() and len(text) > 10 and "SELECT A SIZE" not in text.upper():
                    title = text
                    break
            
            # Match fallback options if specific 'MINI GT' anchor wasn't structural
            if title == "Unknown Mini GT Model" and link_elem.get("title"):
                title = link_elem["title"].strip()

            # Construct clean layout caption metadata block for Telegram notifications
            caption = (
                f"🚨 *NEW MINI GT STOCK DETECTED!* 🚨\n\n"
                f"🚘 *Model:* {title}\n"
                f"💰 *Price:* {price}\n\n"
                f"🔗 *Buy Now:* {product_url}"
            )
            
            send_telegram_photo_alert(img_url, caption)
            processed_count += 1
            
        print(f"Successfully dispatched alert listings for {processed_count} individual Mini GT scale models.")
            
    except Exception as e:
        print(f"An execution error occurred inside the parser parser engine: {e}")

def send_telegram_photo_alert(image_url, caption_text):
    # Switches processing to the native 'sendPhoto' API gateway endpoint
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption_text,
        "parse_mode": "Markdown"
    }
    
    # If a product image URL was found, pass it dynamically. Fallback drops down to raw text send if missing.
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
