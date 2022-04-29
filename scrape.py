from sgselenium import SgFirefox
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

with SgFirefox(block_third_parties=True, is_headless=True) as driver:
    url = "https://baddaddysburgerbar.com/find-us"
    driver.get(url)
    time.sleep(10)
    response = driver.page_source
    print(response)