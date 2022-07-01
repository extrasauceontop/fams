from sgselenium import SgFirefox
from proxyfier import ProxyProviders

with SgFirefox(is_headless=False, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, block_third_parties=False) as driver:
    url = "https://www.brookshires.com/stores/?coordinates=39.84686380709379,-106.87749199999999&zoom=6"
    driver.get(url)
    response = driver.page_source

print(response)
