from sgselenium import SgFirefox
from proxyfier import ProxyProviders
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs

x = 0
while True:
    x = x+1
    if x == 10:
        raise Exception
    url = "https://www.brookshires.com/stores/?coordinates=39.84686380709379,-106.87749199999999&zoom=8"
    try:
        with SgFirefox(is_headless=True, block_third_parties=False, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
            driver.get(url)
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "address1")
                )
            )
            response = driver.page_source
            break
    
    except Exception:
        continue

soup = bs(response, "html.parser")
grids = soup.find_all("store-details-preview", attrs={"aria-controls": "store-details-pane"})
print(len(grids))


