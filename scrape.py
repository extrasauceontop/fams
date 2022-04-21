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
    
    print(driver.page_source)