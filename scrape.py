from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4
from proxyfier import ProxyProviders
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=15,
        granularity=Grain_4(),
    )

    with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, block_third_parties=False) as driver:
        for search_lat, search_lon in search:
            url = (
                "https://api.dineengine.io/burgerfi/custom/dineengine/vendor/olo/restaurants/near?lat="
                + str(search_lat)
                + "&long="
                + str(search_lon)
                + "&radius=3500&limit=1000&calendarstart=20220621&calendarend=20220628"
            )
            driver.get(url)
            response = driver.page_source
            print(response)
            if "Anchorage" in response:
                print("here")
                print("here")
                print("here")
                print("here")
                print("here")
            soup = bs(response, "html.parser")

            locations = soup.find_all("restaurant")
            if len(locations) == 0:
                search.found_nothing()
            for location in locations:
                locator_domain = "burgerfi.com"
                page_url = "https://order.burgerfi.com/menu/" + location["slug"]
                location_name = location["name"]
                latitude = location["latitude"]
                longitude = location["longitude"]
                search.found_location_at(latitude, longitude)
                city = location["city"]
                store_number = location["id"]
                address = location["streetaddress"]
                state = location["state"]
                zipp = location["zip"]
                phone = location["telephone"]
                location_type = "<MISSING>"
                country_code = "US"

                hours_parts = (
                    location.find("calendars").find("ranges").find_all("timerange")
                )
                hours = ""
                for part in hours_parts:
                    day = part["weekday"]
                    sta = part["start"].split(" ")[-1]
                    end = part["end"].split(" ")[-1]

                    hours = hours + day + " " + sta + "-" + end + ", "

                hours = hours[:-2]

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
