from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager


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


def get_data():
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    session = SgRequests()
    start_url = "https://www.dreamdoors.co.uk/kitchen-showrooms"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
    )
    x = 0
    for code in all_codes:
        try:
            formdata = {
                "option": "com_ajax",
                "module": "dreamdoors_store_finder",
                "postcode": code,
                "format": "raw",
            }
            headers = {
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }
            response = session.post(start_url, data=formdata, headers=headers).json()

            try:
                if "error" in response.keys():
                    continue
            except Exception:
                pass

            locator_domain = "dreamdoors.co.uk"
            page_url = response[0]["url"]
            location_name = response[0]["name"]

            driver = get_driver(page_url, "gm-style")

            while True:
                try:
                    page_response = driver.page_source
                    soup = bs(page_response, "html.parser")

                    latitude = page_response.split("?ll=")[1].split(",")[0]
                    longitude = (
                        page_response.split("?ll=")[1].split(",")[1].split("&")[0]
                    )

                    break
                except Exception:
                    continue

            driver.quit()
            address_parts = (
                soup.find("div", attrs={"class": "address"})
                .get_text(strip=True, separator="\n")
                .splitlines()[1:]
            )
            address = address_parts[0]
            zipp = address_parts[-1]

            if len(address_parts) == 3:
                city = address_parts[-2]
                state = "<MISSING>"

            if len(address_parts) == 4:
                city = address_parts[-3]
                state = address_parts[-2]

            if len(address_parts) > 4:
                address = address + " " + address_parts[1]
                city = address_parts[-3]
                state = address_parts[-2]

            x = x + 1

            store_number = response[0]["id"]

            phone = (
                soup.find("div", attrs={"class": "telephone"})
                .find("a")["href"]
                .replace("tel:", "")
            )
            location_type = "<MISSING>"
            times = soup.find_all("span", attrs={"class": "time"})

            y = 0
            hours = ""
            for time_part in times:
                day = days[y]
                y = y + 1
                time = time_part.text.strip()
                hours = hours + day + " " + time + ", "
            country_code = "UK"
            hours = hours[:-2]
            if "coming soon" in address.lower():
                continue

            if city == "Springkerse Industrial Estate":
                address = address + " " + city
                city = state
                state = "<MISSING>"
            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
                "country_code": country_code,
            }
        except Exception:
            pass


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"], is_required=False),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
