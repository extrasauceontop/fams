from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs


url = "https://www.munichsports.com/en/a-coruña-cc-the-style-outlets-en"
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
}

response = session.get(url, headers=headers).text
soup = bs(response, "html.parser")

hours = soup.find("div", attrs={"class": "store-time store-txt"}).text.strip()
print(hours)

with open("file.txt", "w", encoding="utf-8") as output:
    print(response, file=output)