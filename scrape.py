from sgrequests import SgRequests
import ssl
from proxyfier import ProxyProviders

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    "authority": "www.hibbett.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hibbett.com/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

with SgRequests(
    dont_retry_status_codes=([404]), retries_with_fresh_proxy_ip=2, proxy_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER
) as session:
    url = "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/default/Stores-GetNearestStores?latitude=35.8409242&longitude=-78.62285039999999&countryCode=US&distanceUnit=mi&maxdistance=25&social=false"
    response = session.get(url)

print(response.response.text)