from sgselenium import SgChrome, SgSelenium
from proxyfier import ProxyProviders


if __name__ == "__main__":
    url = "https://www.rewe.de/api/marketsearch?searchTerm=311"
    with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        headers = SgSelenium.get_default_headers_for(the_driver=driver, request_url="https://www.rewe.de/")
    
    print(headers["Cookie"])

