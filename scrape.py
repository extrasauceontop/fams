from urllib import response
from sgscrape.sgrecord import SgRecord
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl
from proxyfier import ProxyProviders

ssl._create_default_https_context = ssl._create_unverified_context

def get_data():
    url = "https://www.galerieslafayette.com/m/nos-magasins"

    with SgChrome(proxy_country="fr", proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        driver.get(url)
        response = driver.page_source
        soup = bs(response, "html.parser")
        divs = soup.find_all("div", attrs={"class": "gl-option"})

        for location in divs:
            locator_domain = "https://www.galerieslafayette.com/"
            location_name = location.text.strip()
            page_url = "https://www.galerieslafayette.com/m/magasin-" + location_name.lower().replace(" outlet ", " ").split("lafayette")[1].strip.replace(" ", "-")
            print(page_url)

            latitude = "<LATER>"
            longitude = "<LATER>"
            city = "<LATER>"
            store_number = "<LATER>"
            address = "<LATER>"
            state = "<LATER>"
            zipp = "<LATER>"
            phone = "<LATER>"
            location_type = "<LATER>"
            hours = "<LATER>"
            country_code = "<LATER>"

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