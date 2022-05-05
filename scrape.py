# from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver  # noqa
import undetected_chromedriver as uc
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_driver(url, driver=None):

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(
        # executable_path=ChromeDriverManager().install(), 
        options=options
    )

    driver.get(url)
    return driver

class_name = "eljUma"
url = "https://order.wingzone.com/"

driver = get_driver(url, class_name)
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
