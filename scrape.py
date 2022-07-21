from sgselenium import MagiConfig
from proxyfier import ProxyProviders


url = "https://www.hoogvliet.com/"
MagiConfig.find_sgselenium(url, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) 

