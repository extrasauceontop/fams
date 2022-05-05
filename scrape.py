from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import time
import json


user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
url = "https://order.wingzone.com/"

with SgChrome(executable_path=ChromeDriverManager().install(), user_agent=user_agent, is_headless=True, extra_option_args=["start-maximized"]).driver() as driver:
    driver.get(url)
    time.sleep(2)
    driver.find_elements_by_class_name("styles__StyledPrimaryButton-sc-3mz1a9-0")[1].click()
    time.sleep(2)
    response = driver.page_source

    data = driver.execute_async_script(
        """
        var done = arguments[0]
        fetch("https://api.koala.io/v1/ordering/store-locations/?sort[state_id]=asc&sort[label]=asc&include[]=operating_hours&include[]=attributes&include[]=delivery_hours&paginate=false", {
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": null,
            "method": "GET",
            "mode": "cors",
            "credentials": "omit"
        })
        .then(res => res.json())
        .then(data => done(data))
        """
    )

print(data)
