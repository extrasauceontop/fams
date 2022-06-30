from sgrequests import SgRequests

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

with SgRequests() as session:
    url = "https://fastpaydayloansfloridainc.com/sitemap"
    response = session.get(url, headers=HEADERS).text

print(response)