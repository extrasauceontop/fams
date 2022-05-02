from bs4 import BeautifulSoup as bs
from sgselenium.sgselenium import SgChrome
from sgscrape import simple_scraper_pipeline as sp
import html
import json
import ssl
from webdriver_manager.chrome import ChromeDriverManager
import time

ssl._create_default_https_context = ssl._create_unverified_context


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent=user_agent,
        is_headless=True,
    ).driver() as driver:
        driver.get(
            "https://api.dineengine.io/baddaddys/items/custom_pages?fields%5B0%5D=%2A.%2A.%2A.%2A&single=false&limit=-1"
        )
        time.sleep(20)
        print(driver.page_source)
        soup = bs(
            html.unescape(extract_json(driver.page_source)[0]["data"][6]["content"]),
            "html.parser",
        )

    grids = soup.find_all("div", attrs={"class": "h-fit-content"})
    for grid in grids:
        locator_domain = "baddaddysburgerbar.com"
        page_url = (
            grid.find_all("a")[-1]["href"]
            .replace("menu", "locations")
            .replace("order.", "")
        )
        location_name = grid.find("div").find("div").text.strip()
        address = grid.find("div").find_all("div")[1].text.strip()
        city = grid.find("div").find_all("div")[2].text.strip().split(", ")[0]
        state = (
            grid.find("div")
            .find_all("div")[2]
            .text.strip()
            .split(", ")[1]
            .split(" ")[0]
        )
        zipp = (
            grid.find("div")
            .find_all("div")[2]
            .text.strip()
            .split(", ")[1]
            .split(" ")[1]
        )
        phone = (
            grid.find("div", attrs={"class": "pb-3"})
            .find("a")["href"]
            .replace("tel:", "")
        )
        location_type = "<MISSING>"
        country_code = "US"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        store_number = "<MISSING>"

        hours_parts = (
            grid.find("div", attrs={"class": "pb-3"}).text.strip().replace("\n", "")
        )
        while "  " in hours_parts:
            hours_parts = hours_parts.replace("  ", " ")

        hours = hours_parts.split(phone[-3:])[1].replace(" ", "")

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
