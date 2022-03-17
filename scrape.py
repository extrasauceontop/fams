from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgpostal.sgpostal import parse_address_intl
from sglogging import sglog
import ssl
import time
from bs4 import BeautifulSoup as bs

ssl._create_default_https_context = ssl._create_unverified_context
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}
log = sglog.SgLogSetup().get_logger(logger_name="carehomes")


def get_page_urls():
    start_url = "https://headquartersoffice.com/page/"
    x = 0

    final_links = []
    while True:
        x = x + 1
        url = start_url + str(x) + "/?s"

        try:
            response = session.get(url, headers=headers).text

        except Exception:
            log.info(url)
            break
        if "looks like nothing was found at this location" in response:
            break

        soup = bs(response, "html.parser")
        testings = soup.find_all("h2", attrs={"class": "entry-title"})
        for test in testings:
            if (
                test.find("a").text.strip()[0].isalpha() is False
                or test.find("a").text.strip()[0] == "("
            ):
                try:
                    log.info(test.find("a").text.strip())
                    log.info(test.find("a")["href"])

                except Exception:
                    log.info(test.find("a")["href"])

                log.info("")
                log.info("")

        links = [
            h2_tag.find("a")["href"]
            for h2_tag in soup.find_all("h2", attrs={"class": "entry-title"})
            if h2_tag.find("a").text.strip()[0].isalpha() is True
            or h2_tag.find("a").text.strip()[0] == "("
        ]

        for link in links:
            final_links.append(link)

    return final_links


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

    driver.maximize_window()
    return driver


def new_map_page(driver):
    locations = []
    while True:
        try:
            element = driver.find_element_by_class_name(
                "paginationjs-next.J-paginationjs-next"
            ).find_element_by_css_selector("a")
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)

        except Exception:
            break

    test = driver.execute_script(
        "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
    )

    responses = []
    for item in test:
        if "base64" in item["name"] and "marker-list" in item["name"]:
            response = session.get(item["name"]).json()
            responses.append(response)

    for response in responses:
        for location in response["meta"]:
            locator_domain = "https://headquartersoffice.com/"
            page_url = driver.current_url
            latitude = location["lat"]
            longitude = location["lng"]

            store_number = location["id"]
            full_address = location["address"]

            if "+" in full_address:
                full_address = "".join(
                    part + " " for part in full_address.split(" ")[1:]
                )

            if latitude in full_address and longitude in full_address:
                city = "<MISSING>"
                address = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                country_code = "<MISSING>"
                full_address = "<MISSING>"

            if full_address != "<MISSING>":
                addr = parse_address_intl(full_address)
                city = addr.city
                if city is None:
                    city = "<MISSING>"

                address_1 = addr.street_address_1
                address_2 = addr.street_address_2

                if address_1 is None and address_2 is None:
                    address = "<MISSING>"
                else:
                    address = (str(address_1) + " " + str(address_2)).strip()

                state = addr.state
                if state is None:
                    state = "<MISSING>"

                zipp = addr.postcode
                if zipp is None:
                    zipp = "<MISSING>"

                country_code = addr.country
                if country_code is None:
                    country_code = "<MISSING>"

            phone = "<MISSING>"

            if page_url[-1] == "/":
                page_url = page_url[:-1]
            location_type = page_url.split("/")[-1]
            hours = "<MISSING>"
            location_name = location_type.replace("-", " ")
            locations.append(
                {
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
            )

    return locations


def old_map_page(driver):
    locations = []
    test = driver.execute_script(
        "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
    )
    for item in test:
        if "base64" in item["name"]:

            session = SgRequests()
            url = item["name"]
            try:
                response = session.get(url).json()

            except Exception:
                continue

            if "markers" in response.keys():
                break

    try:
        if response is None:
            log.info(driver.current_url)
            raise Exception

    except Exception:
        log.info(driver.current_url)
        raise Exception
    for location in response["markers"]:
        locator_domain = "https://headquartersoffice.com/"
        page_url = driver.current_url
        location_name = location["title"]
        latitude = location["lat"]
        longitude = location["lng"]
        store_number = location["id"]

        phone = "<MISSING>"
        for field in location["custom_field_data"]:
            if "phone" in field["name"].lower():
                phone = field["value"].replace("+", "")

        if page_url[-1] == "/":
            page_url = page_url[:-1]
        location_type = page_url.split("/")[-1]
        hours = "<MISSING>"

        full_address = "lost"
        for field in location["custom_field_data"]:
            if "address" in field["name"].lower():
                full_address = field["value"].replace("+", "")

        if full_address == "lost":
            full_address = location["address"]

        if "+" in full_address.split(" ")[0]:
            full_address = "".join(part + " " for part in full_address.split(" ")[1:])

        if full_address != "lost":
            addr = parse_address_intl(full_address)
            city = addr.city
            if city is None:
                city = "<MISSING>"

            address_1 = addr.street_address_1
            address_2 = addr.street_address_2

            if address_1 is None and address_2 is None:
                address = "<MISSING>"
            else:
                address = (str(address_1) + " " + str(address_2)).strip()

            state = addr.state
            if state is None:
                state = "<MISSING>"

            zipp = addr.postcode
            if zipp is None:
                zipp = "<MISSING>"

            country_code = addr.country
            if country_code is None:
                country_code = "<MISSING>"

        else:
            city = "<MISSING>"
            address = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "<MISSING>"

        locations.append(
            {
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
        )

    return locations


def get_data():
    page_urls = get_page_urls()
    x = 0
    y = 0
    for page_url in page_urls:
        if page_url == page_urls[0]:
            driver = get_driver(page_url, "inside-page-hero")

        else:
            try:
                driver.get(page_url)

            except Exception:
                driver = get_driver(page_url, "inside-page-hero", driver=driver)

        response = driver.page_source
        soup = bs(response, "html.parser")

        map_object = soup.find("div", attrs={"class": "wpgmza_map"})
        if map_object is None:
            if (
                page_url == "https://headquartersoffice.com/privacy/"
                or page_url == "https://headquartersoffice.com/"
                or "?" in soup.find("h1").text.strip()
            ):
                continue

            locator_domain = "headquartersoffice.com"
            location_name = soup.find("h1").text.strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            city = "<INACCESSIBLE"
            store_number = "<MISSING>"
            address = "<INACCESSIBLE>"
            state = "<INACCESSIBLE>"
            zipp = "<INACCESSIBLE>"
            phone = "<INACCESSIBLE>"
            location_type = "<INACCESSIBLE>"
            hours = "<MISSING>"
            country_code = "<MISSING>"

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

        else:
            time.sleep(1)
            test = driver.execute_script(
                "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
            )

            found = 0
            for item in test:
                if "base64" in item["name"] and "marker-list" in item["name"]:
                    x = x + 1
                    locations = new_map_page(driver)
                    found = 1
                    if len(locations) == 0:
                        log.info("")
                        log.info("new map")
                        log.info(driver.current_url)
                    for loc in locations:
                        yield loc

                    break

            if found == 0:
                locations = old_map_page(driver)
                if len(locations) == 0:
                    log.info("")
                    log.info("old map")
                    log.info(driver.current_url)
                for loc in locations:
                    yield loc
                y = y + 1

    log.info(x)
    log.info(y)


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
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
