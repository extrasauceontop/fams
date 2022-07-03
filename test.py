from sgselenium import SgFirefox
from proxyfier import ProxyProviders
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.brookshires.com/stores/?coordinates=39.84686380709379,-106.87749199999999&zoom=8"
with SgFirefox(is_headless=False, block_third_parties=True, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
    driver.get(url)
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "address1")
        )
    )
    response = driver.page_source

with open("file.txt", "w", encoding="utf-8") as output:
    print(response, file=output)

