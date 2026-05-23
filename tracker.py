import requests
from bs4 import BeautifulSoup
import os
import json
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent":"Mozilla/5.0"
}

SEEN_FILE = "seen.json"

try:
    with open(SEEN_FILE,"r") as f:
        seen = set(json.load(f))
except:
    seen = set()

def send(msg):
    r=requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id":CHAT_ID,
            "text":msg
