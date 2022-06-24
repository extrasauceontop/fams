from sgselenium import SgFirefox
from proxyfier import ProxyProviders

url = "https://www.dominospizza.es/tiendas-dominos-pizza"
proxy_url = "https://www.galerieslafayette.com/m/nos-magasins"
with SgFirefox(proxy_country="es", proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
    try:
        driver.get(proxy_url)
    except Exception: pass
    driver.get(url)
    response = driver.page_source


print(response)
