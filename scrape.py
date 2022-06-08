from sgselenium import SgChrome
from proxyfier import ProxyProviders
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
    with SgChrome(block_third_parties=True, is_headless=True, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, proxy_country="gr") as driver:
        url = "https://mcdonalds.gr/%ce%b5%cf%83%cf%84%ce%b9%ce%b1%cf%84%cf%8c%cf%81%ce%b9%ce%b1/"
        driver.get(url)
        class_name = "elementor-item"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        print("here")
        data = driver.execute_async_script(
            """
            var done = arguments[0]
            fetch("https://mcdonalds.gr/wp-admin/admin-ajax.php", {
            "headers": {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest"
            },
            "referrer": "https://mcdonalds.gr/%ce%b5%cf%83%cf%84%ce%b9%ce%b1%cf%84%cf%8c%cf%81%ce%b9%ce%b1/",
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": "action=get_locations&token=8866b76e03",
            "method": "POST",
            "mode": "cors",
            "credentials": "include"
            })
            .then(res => res.json())
            .then(data => done(data))
            """
        )

        print(data)

