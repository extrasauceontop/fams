from sgselenium.sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8
from sgscrape import simple_scraper_pipeline as sp
import json
from bs4 import BeautifulSoup as bs
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_8(),
        max_search_distance_miles=100,
    )

    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
        block_third_parties=False,
    ) as driver:

        for zip_code in search:
            data_url = (
                "https://prismahealth.org/api/search/search?pageSize=100&pageNumber=1&searchType=location&zip="
                + zip_code
                + "&radius=1000"
            )

            driver.get(data_url)
            source = driver.page_source
            soup = bs(source, "html.parser")
            text = soup.text.strip()
            response_json = json.loads(text)

            locations = response_json["Items"]

            if len(locations) == 0:
                search.found_nothing()

            for location in locations:
                locator_domain = "prismahealth.org"
                page_url = data_url
                location_name = location["Title"]
                print(location_name)
                address = location["Address"][0] + " " + location["Address"][1]

                city = location["Address"][2].split(",")[0]
                state = location["Address"][2].split(" ")[-2]
                zipp = location["Address"][2].split(" ")[-1]
                country_code = "US"
                store_number = location["Id"].split(";")[0]

                phone = location["Phone"]
                location_type = "<MISSING>"
                latitude = location["Coordinate"]["Latitude"]
                longitude = location["Coordinate"]["Longitude"]
                search.found_location_at(latitude, longitude)
                hours = "<MISSING>"

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
        page_url=sp.MappingField(mapping=["page_url"]),
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
        duplicate_streak_failure_factor=-1,
    )
    pipeline.run()


if __name__ == "__main__":
    scrape()
