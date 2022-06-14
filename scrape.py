from sgselenium import SgFirefox
from proxyfier import ProxyProviders

url = "https://www.galerieslafayette.com/"
with SgFirefox(is_headless=True, block_third_parties=False, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
    driver.get(url)
    response = driver.page_source
    
with open("file.txt", "w", encoding="utf-8") as output:
    print(response)