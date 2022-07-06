from sgselenium import SgFirefox
import time

url = "https://www.bravissimo.com/us/shops/all/"
with SgFirefox(is_headless=True) as driver:
    driver.get(url)
    time.sleep(10)
    response = driver.page_source


print(response)