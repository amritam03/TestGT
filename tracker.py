import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Main Mini GT Collection Grid URL
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
        
        # KarzAndDolls structures grid columns using standard Bootstrap layouts
        product_cards = soup.select(".product-box") or soup.select("[class*='col-']") or soup.find_all("div", class_=lambda c: c and "product" in c.lower())
        
        print(f"Scan running. Processing grid container elements...")
        processed_count = 0

        for card in product_cards:
            # 1. Price Verification: Ensures it's a real, listed item block
            price_elem = card.find(string=lambda text: text and any(marker in text for marker in ["Rs.", "₹"]))
            if not price_elem:
                continue
            price = price_elem.strip()
            
            # 2. Extract Image URL 
            img_elem = card.find("img")
            img_url = None
            if img_elem:
                img_src = img_elem.get("data-src") or img_elem.get("src")
                if img_src:
                    img_url = urljoin("https://www.karzanddolls.com", img_src)
            
            # 3. Clean Title & Extract The Target Link
            # We filter elements specifically to look for the one containing the item name string.
            title = "Unknown Mini GT Model"
            product_url = TARGET_URL  # Fallback if specific link fails
            
            # We look closely at anchor tags that wrap headers or contain longer text titles
            links_in_card = card.find_all("a", href=True)
            for a_tag in links_in_card:
                text = a_tag.get_text(strip=True)
                
                # The valid product link tag contains the 'MINI GT' name or specific model markers
                if "MINI GT" in text.upper() and len(text) > 8 and "SELECT A SIZE" not in text.upper():
                    title = text
                    product_url = urljoin("https://www.karzanddolls.com", a_tag["href"])
                    break
                    
            # Fallback title/link check using image context structural layout if text anchor extraction failed
            if title == "Unknown Mini GT Model" and img_elem:
                parent_a = img_elem.find_parent("a", href=True)
                if parent_a:
                    product_url = urljoin("https://www.karzanddolls.com", parent_a["href"])
                if img_elem.get("alt"):
                    title = img_elem["alt"].strip()

            # Prevent rendering structural anomalies that lack proper links
            if "javascript" in product_url.lower() or product_url == "https://www.karzanddolls.com":
                continue

            # Format caption string layout for Telegram channel
            caption = (
                f"🚨 *NEW MINI GT STOCK DETECTED!* 🚨\n\n"
                f"🚘 *Model:* {title}\n"
                f"💰 *Price:* {price}\n\n"
                f"🔗 *Buy Now:* {product_url}"
            )
            
            send_telegram_photo_alert(img_url, caption)
            processed_count += 1
            
        print(f"Successfully processed and generated alert listings for {processed_count} individual models.")
            
    except Exception as e:
        print(f"An execution error occurred inside the parser parser engine: {e}")

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
