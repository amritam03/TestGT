import requests
from bs4 import BeautifulSoup

URL = "https://www.karzanddolls.com/details/mini+gt+/mini-gt/MTY1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers)

print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)
    href = a["href"]

    full = href
    if href.startswith("/"):
        full = "https://www.karzanddolls.com" + href

    # Skip obvious menu links
    if "/shop/" in full:
        continue

    # Show only detail pages
    if "/details/" not in full:
        continue

    # Ignore Mini GT category pages
    if "/mini-gt/MTY1" in full:
        continue

    print("TEXT:", text[:150])
    print("LINK:", full)
    print("------")
