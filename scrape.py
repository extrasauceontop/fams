from sgselenium.sgselenium import SgChrome
import ssl
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp

ssl._create_default_https_context = ssl._create_unverified_context


def clean_phone(text):
    text = text.lower()
    replace_list = ["(", ")", ".", "tel", ":", "+"]
    black_list = ["e", "x", "d"]
    for r in replace_list:
        text = text.replace(r, "").strip()
    for b in black_list:
        if b in text:
            text = text.split(b)[0].strip()

    return text

def get_data():
    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ) as driver:
        driver.get("https://www.bobbibrowncosmetics.com/store_locator")

        # with open("file.txt", "w", encoding="utf-8") as output:
        #     print(driver.page_source, file=output)

        data = driver.execute_async_script(
            """
            var done = arguments[0]
            fetch("https://www.bobbibrowncosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents", {
                "headers": {
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "sec-ch-ua-mobile": "?0",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-csrf-token": "e68159e13a31f32e77908f9a81c12242400f5e30,bb911c138a1703774f09d2aaf872bac27342d747,1650567711",
                    "x-requested-with": "XMLHttpRequest"
                },
                "referrer": "https://www.bobbibrowncosmetics.com/store_locator",
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": 'JSONRPC=[{"method":"locator.doorsandevents","id":2,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, STORE_TYPE, LONGITUDE, LATITUDE","radius":"","country":"United States","region_id":"0,47,27","latitude":33.0218117,"longitude":-97.12516989999999,"uom":"mile","_TOKEN":"b6a2036fda64fc609a1f77f72fcef03bdccde0f9,df93f53a98d3eac0d569475de97dc8d9e8fd3543,1650031353"}]}]',
                "method": "POST",
                "mode": "cors",
                "credentials": "include"
            })
            .then(res => res.json())
            .then(data => done(data))
            """
        )

        for store_number in data[0]["result"]["value"]["doors"]:
            locator_domain = "bobbibrowncosmetics.com"
            page_url = "https://www.bobbibrowncosmetics.com/store_locator"
            
            location = data[0]["result"]["value"]["results"][str(store_number)]
            location_name = location["DOORNAME"]
            latitude = location["LATITUDE"]
            longitude = location["LONGITUDE"]
            city = location["CITY"]
            address = location["ADDRESS"]
            state = location["REGION"]
            zipp = location["ZIP_OR_POSTAL"]
            phone = clean_phone(location["PHONE1"])
            location_type = location["STORE_TYPE"]
            hours = location["STORE_HOURS"]
            country_code = location["COUNTRY"]

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
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], is_required=False
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"], is_required=False
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
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