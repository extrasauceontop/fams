from sgselenium import SgChrome
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
with SgChrome() as driver:
    driver.get("https://www.zorbaz.com/")
    driver.save_screenshot("zorbas.png")
    response = driver.page_source
    print(response)
