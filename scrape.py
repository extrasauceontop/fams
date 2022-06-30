from sgrequests import SgRequests

with SgRequests() as session:
    url = "https://fastpaydayloansfloridainc.com/sitemap"
    response = session.get(url).text

print(response)