from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgrequests import SgRequests
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def reset_sessions(data_url):
    s = SgRequests()

    driver = get_driver(data_url, "main-menu__tab-button")

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                driver.quit()
                return [s, headers, response_text]

        except Exception:
            driver.quit()
            continue


url = "https://www.amegybank.com/"
response = reset_sessions(url)[2]

print(response)