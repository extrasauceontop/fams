from sgselenium import SgChrome
from proxyfier import ProxyProviders
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
    with SgChrome(block_third_parties=False, is_headless=True, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, proxy_country="gr") as driver:
        url = "https://mcdonalds.gr/%ce%b5%cf%83%cf%84%ce%b9%ce%b1%cf%84%cf%8c%cf%81%ce%b9%ce%b1/"
        driver.get(url)
        time.sleep(10)
        response = driver.page_source

        print(response)