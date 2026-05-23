import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

r = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "🎉 GitHub + Telegram finally connected!"
    }
)

print("STATUS:", r.status_code)
print("RESPONSE:", r.text)
