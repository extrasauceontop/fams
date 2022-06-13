from sgselenium import SgChrome
import time
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    with SgChrome(is_headless=True, block_third_parties=True) as driver:
        time.sleep(2)
        buttons = driver.find_elements_by_class_name('button')
        for button in buttons:
            if "view all locations" in button.text.lower():
                button.click()
                print("here")
                break
        time.sleep(2)

        data = driver.execute_async_script(
            """
            var done = arguments[0]
            fetch("https://api.koala.io/v1/ordering/store-locations/?sort[state_id]=asc&sort[label]=asc&include[]=operating_hours&include[]=attributes&include[]=delivery_hours&paginate=false", {
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": null,
                "method": "GET",
                "mode": "cors",
                "credentials": "omit"
            })
            .then(res => res.json())
            .then(data => done(data))
            """
        )


        print(data)

    for location in data["data"]:
        locator_domain = "wingzone.com"
        page_url = "https://order.wingzone.com/"
        location_name = location["cached_data"]["label"]
        latitude = location["cached_data"]["latitude"]
        longitude = location["cached_data"]["longitude"]
        city = location["cached_data"]["city"]
        store_number = location["id"]
        address = location["street_address"]
        state = location["cached_data"]["state"]
        zipp = location["cached_data"]["zip"]
        phone = location["cached_data"]["phone_number"]
        location_type = "<MISSING>"
        country_code = "US"

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


if __name__ == "__main__":
    scrape()

# "sc-7d5fe5c2-0.sc-e1bb3b0d-6.jmEYpy.yYTef"
# "sc-7d5fe5c2-0 sc-e1bb3b0d-6 jmEYpy yYTef"