from sgselenium import SgChrome
from proxyfier import ProxyProviders

url = "https://www.brookshires.com/stores/?coordinates=39.84686380709379,-106.87749199999999&zoom=6"
if __name__ == "__main__":
    with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, block_third_parties=True) as driver:
        driver.get(url)
        response = driver.page_source

    # with open("file.txt", "w", encoding="utf-8") as output:
    print(response, file=output)