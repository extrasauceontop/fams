from sgselenium import SgChrome
from proxyfier import ProxyProviders

if __name__ == "__main__":
    url = "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/default/Stores-GetNearestStores?latitude=33.4306545&longitude=-86.7919009&countryCode=US&distanceUnit=mi&maxdistance=25&social=false"
    with SgChrome(block_third_parties=False, is_headless=False, block_javascript=False, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        driver.get(url)
        response = driver.page_source

        print(response)
