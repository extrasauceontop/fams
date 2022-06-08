from sgselenium import SgChrome
from proxyfier import ProxyProviders
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
    with SgChrome(block_third_parties=True, is_headless=True, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, proxy_country="gr") as driver:
        url = "https://mcdonalds.gr/%ce%b5%cf%83%cf%84%ce%b9%ce%b1%cf%84%cf%8c%cf%81%ce%b9%ce%b1/"
        driver.get(url)
        time.sleep(10)

        data = driver.execute_async_script(
            """
            var done = arguments[0]
            fetch("https://mcdonalds.gr/wp-admin/admin-ajax.php", {
            "headers": {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
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

