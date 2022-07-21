from sgselenium import SgFirefox
from proxyfier import ProxyProviders

if __name__ == "__main__":
    
    def check_response(request):
        response = driver.page_source
        if len(response.split("div")) > 2:
            return True
        
        else:
            return False

    url = "https://www.hoogvliet.com/"
    with SgFirefox(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, is_headless=True) as driver:
        driver.get(url)
        response = driver.page_source

    print(response)