from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    initial_url = "https://www.sytner.co.uk/dealer-locator/?postcode=london&distance=0&franchiseHash="

    with SgChrome() as driver:
        driver.get(initial_url)

        html = driver.page_source

        soup = bs(html, "html.parser")

        grids = soup.find_all("div", attrs={"class": "row-fluid row-t2crq"})
        for grid in grids:
            locator_domain = "sytner.co.uk"
            page_url = "https:" + grid.find("a", attrs={"title": "Full Details"})["href"]
            location_name = grid.find("h3").text.strip()
            address = grid.find("span", attrs={"class": "address-line1"}).text.strip()[:-1]
            city = grid.find("span", attrs={"class": "address-city"}).text.strip()[:-1]
            state = grid.find("span", attrs={"class": "address-county"}).text.strip()[:-1]
            zipp = grid.find("span", attrs={"class": "address-postcode"}).text.strip()
            country_code = "UK"
            phone = grid.find("div", attrs={"class": "location-no"}).find("a")["href"]
            phone = phone.split(":")[1]

            location_type = grid.find("span").text.strip()
            latitude = grid.find("a", attrs={"title": "View Location"})["data-latitude"]
            longitude = grid.find("a", attrs={"title": "View Location"})["data-longitude"]
            store_number = grid.find("a", attrs={"title": "View Location"})["data-id"]
            
            driver.get(page_url)
            hours_response = driver.page_source

            print(hours_response)
            # print(page_url)
            
            raise Exception
            hours = "<LATER>"

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
