from sgselenium import *
from proxyfier import ProxyProviders

with SgFirefox(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, driver_wait_timeout=300) as driver:
    req = driver.get_and_wait_for_request("https://www.extendedstayamerica.com/hotels/")
    print(req.response)