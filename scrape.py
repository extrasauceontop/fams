from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
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
    
    driver.maximize_window()
    return driver


def old_map_page(driver):

    test = driver.execute_script("var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")
    for item in test:
        if "base64" in item["name"]:

            session = SgRequests()
            url = item["name"]
            response = session.get(url).json()

            if "markers" in response.keys():
                break

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


def get_data():
    page_url = "https://headquartersoffice.com/verizon/"
    driver = get_driver(page_url, "inside-page-hero")

    locations = old_map_page(driver)


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