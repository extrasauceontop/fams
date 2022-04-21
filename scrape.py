from sgselenium.sgselenium import SgChrome
import ssl
from webdriver_manager.chrome import ChromeDriverManager

ssl._create_default_https_context = ssl._create_unverified_context

with SgChrome(
    executable_path=ChromeDriverManager().install(),
    user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    is_headless=True,
) as driver:
    driver.get("https://www.bobbibrowncosmetics.com/store_locator")

    # with open("file.txt", "w", encoding="utf-8") as output:
    #     print(driver.page_source, file=output)

    data = driver.execute_async_script(
        """
        var done = arguments[0]
        fetch("https://www.bobbibrowncosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents", {
            "headers": {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-csrf-token": "e68159e13a31f32e77908f9a81c12242400f5e30,bb911c138a1703774f09d2aaf872bac27342d747,1650567711",
                "x-requested-with": "XMLHttpRequest"
            },
            "referrer": "https://www.bobbibrowncosmetics.com/store_locator",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A3%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+DOORNAME%2C+EVENT_NAME%2C+EVENT_START_DATE%2C+EVENT_END_DATE%2C+EVENT_IMAGE%2C+EVENT_FEATURES%2C+EVENT_TIMES%2C+SERVICES%2C+STORE_HOURS%2C+ADDRESS%2C+ADDRESS2%2C+STATE_OR_PROVINCE%2C+CITY%2C+REGION%2C+COUNTRY%2C+ZIP_OR_POSTAL%2C+PHONE1%2C+STORE_TYPE%2C+LONGITUDE%2C+LATITUDE%22%2C%22radius%22%3A50%2C%22country%22%3A%22United+States%22%2C%22region_id%22%3A%220%2C47%2C27%22%2C%22latitude%22%3A40.75368539999999%2C%22longitude%22%3A-73.9991637%2C%22uom%22%3A%22mile%22%2C%22_TOKEN%22%3A%22e68159e13a31f32e77908f9a81c12242400f5e30%2Cbb911c138a1703774f09d2aaf872bac27342d747%2C1650567711%22%7D%5D%7D%5D",
            "method": "POST",
            "mode": "cors",
            "credentials": "include"
        })
        .then(res => res.json())
        .then(data => done(data))
        """
    )

    # with open("file.txt", "w", encoding="utf-8") as output:
    #     print(data, file=output)

    print(data)