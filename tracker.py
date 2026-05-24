import os
import sys
import requests
from bs4 import BeautifulSoup

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
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Server returned status code: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # FIX: Track active item listings by counting blocks containing price points (Rs. or ₹)
        product_prices = soup.find_all(string=lambda text: text and any(marker in text for marker in ["Rs.", "₹"]))
        current_count = len(product_prices)
        
        print(f"Scan complete. Active Mini GT items with price tags found: {current_count}")
        
        # Change this to > 0 to test your Telegram ping immediately.
        # Once verified, you can set it to track if the count increases!
        if current_count > 0: 
            msg = f"🚨 *MINI GT STOCK DETECTED!* 🚨\n\nFound *{current_count}* listed items in the catalog.\n\nHunt here: {TARGET_URL}"
            send_telegram_alert(msg)
            
    except Exception as e:
        print(f"An error occurred: {e}")

def send_telegram_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        res = requests.post(telegram_url, json=payload, timeout=10)
        if res.status_code == 200:
            print("Alert successfully sent to Telegram!")
        else:
            print(f"Telegram API Error: {res.status_code}")
    except Exception as e:
        print(f"Failed to send alert: {e}")

if __name__ == "__main__":
    check_restock()
