from sgselenium import SgFirefox
import time

url = "https://www.galeria.de/filialen/l"
with SgFirefox(is_headless=True) as driver:
    driver.get(url)
    time.sleep(10)
    response = driver.page_source

print(response)