from sgselenium import SgChrome
from proxyfier import ProxyProviders

if __name__ == "__main__":
    url = "https://nomnom-prod-api.pieology.com/restaurants/near?lat=35.7796&long=-78.6382&radius=100&limit=500&nomnom=calendars&nomnomcalendar_from=20220705&nomnom_calendars_to=20220711&nomnom_exclude_extref=999"
    with SgChrome(block_third_parties=False, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        driver.get(url)
        response = driver.page_source

    print(response)