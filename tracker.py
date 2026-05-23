import requests
from bs4 import BeautifulSoup

URL = "https://www.karzanddolls.com/details/tsm%2Bmodel%2Bcars/mini-gt/MTY1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a", href=True)

print("Total links:", len(links))

for i, a in enumerate(links[:50]):   # first 50 only
    text = a.get_text(" ", strip=True)
    href = a["href"]

    print("\n-----")
    print("TEXT:", text[:100])
    print("LINK:", href)
