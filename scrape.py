from sgselenium import SgFirefox
import ssl
from proxyfier import ProxyProviders

ssl._create_default_https_context = ssl._create_unverified_context



url = "https://www.hibbett.com/stores"
with SgFirefox(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, block_third_parties=True) as driver:
    driver.get(url)
    response = driver.page_source

print(response)