from sgselenium.sgselenium import SgFirefox
import ssl
from proxyfier import ProxyProviders

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/default/Stores-GetNearestStores?latitude=35.8409242&longitude=-78.62285039999999&countryCode=US&distanceUnit=mi&maxdistance=25&social=false"
with SgFirefox(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, block_third_parties=False) as driver:
    driver.get(url)
    response = driver.page_source

print(response)