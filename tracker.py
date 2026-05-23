import requests
import os

BOT_TOKEN = os.getenv("8983135704:AAEPecaHWbRY7Rej3fKaC2_JeeKYZPAzQHw")
CHAT_ID = os.getenv("982948994")

print("BOT:", BOT_TOKEN[:10] if BOT_TOKEN else "missing")
print("CHAT:", CHAT_ID)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

r = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "✅ GitHub Actions test message"
    }
)

print("Status:", r.status_code)
print("Response:", r.text)
