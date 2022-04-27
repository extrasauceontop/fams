from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgFirefox
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    url = "https://baddaddysburgerbar.com/find-us"
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    x = 0
    while True:
        x = x+1
        if x == 10:
            raise Exception
        try:
            driver = SgFirefox(user_agent=user_agent, is_headless=True).driver()
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "text-color-primary"))
            )
            response = driver.page_source

            break
        except Exception as e:
            with open("file.txt", "w", encoding="utf-8") as output:
                print(driver.page_source, file=output)

            continue

    soup = bs(response, "html.parser")
    grids = soup.find_all("div", attrs={"class": "h-fit-content"})
    for grid in grids:
        locator_domain = "baddaddysburgerbar.com"
        page_url = grid.find_all("a")[-1]["href"]
        location_name = grid.find("div").find("div").text.strip()
        address = grid.find("div").find_all("div")[1].text.strip()
        city = grid.find("div").find_all("div")[2].text.strip().split(", ")[0]
        state = grid.find("div").find_all("div")[2].text.strip().split(", ")[1].split(" ")[0]
        zipp = grid.find("div").find_all("div")[2].text.strip().split(", ")[1].split(" ")[1]
        phone = grid.find("div", attrs={"class": "pb-3"}).find("a")["href"].replace("tel:", "")
        location_type = "<MISSING>"
        country_code = "US"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        store_number = "<MISSING>"

        hours_parts = grid.find("div", attrs={"class": "pb-3"}).text.strip().replace("\n", "")
        while "  " in hours_parts:
            hours_parts = hours_parts.replace("  ", " ")

        hours_parts = hours_parts.split(phone[-3:])[1]
        print(hours_parts)
        
        hours = "MM"

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