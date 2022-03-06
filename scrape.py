from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp
import ast
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
search = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN])

hours_key_list = [
    ["MonOpen", "MonClose"],
    ["TueOpen", "TueClose"],
    ["WedOpen", "WedClose"],
    ["ThuOpen", "ThuClose"],
    ["FriOpen", "FriClose"],
    ["SatOpen", "SatClose"],
    ["SunOpen", "SunClose"],
]


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
    return driver


def get_data():
    search = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN])

    hours_key_list = [
        ["MonOpen", "MonClose"],
        ["TueOpen", "TueClose"],
        ["WedOpen", "WedClose"],
        ["ThuOpen", "ThuClose"],
        ["FriOpen", "FriClose"],
        ["SatOpen", "SatClose"],
        ["SunOpen", "SunClose"],
    ]
    driver = get_driver("https://www.schuh.co.uk/stores/", "secondLine")

    for search_lat, search_lon in search:
        while True:
            try:
                data = driver.execute_async_script(
                    r"""
                    var done = arguments[0]
                    fetch('https://schuhservice.schuh.co.uk/StoreFinderService/GetNearbyBranchesByLocation', {
                "headers": {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "no-cache",
                    "content-type": "application/json;charset=UTF-8;",
                    "sec-ch-ua-mobile": "?0",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site"
                },
                "referrer": "https://www.schuh.co.uk/",
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": '{"lat":"""
                    + str(search_lat)
                    + r""","lon":"""
                    + str(search_lon)
                    + r""","culture":"en-gb"}',
                "method": "POST",
                "mode": "cors",
                "credentials": "include"
                    })
                    .then(res => res.json())
                    .then(data => done(data))
                    """
                )
                break
            except Exception:
                driver = get_driver(
                    "https://www.schuh.co.uk/stores/", "secondLine", driver=driver
                )
                continue

        data = data["d"]
        data = (
            data.replace('"', "'")
            .replace("true", "True")
            .replace("false", "False")
            .replace("'s", "s")
        )

        try:
            data = ast.literal_eval(data)
        except Exception:
            continue

        for location in data:
            locator_domain = "schuh.co.uk"
            page_url = "https://www.schuh.co.uk/stores/" + location[
                "BranchName"
            ].lower().replace(" ", "-")
            location_name = location["BranchName"]
            city = location["BranchCity"]
            zipp = location["BranchPostcode"]
            country_code = "UK"
            store_number = location["BranchRef"]
            phone = location["BranchPhone"]
            latitude = location["BranchLatitude"]
            longitude = location["BranchLongitude"]

            while True:
                try:
                    location_data = driver.execute_async_script(
                        r"""
                        var done = arguments[0]
                        fetch("https://schuhservice.schuh.co.uk/StoreFinderService/GetAdditionalBranchInfo", {
                        "headers": {
                            "accept": "application/json, text/javascript, */*; q=0.01",
                            "accept-language": "en-US,en;q=0.9",
                            "cache-control": "no-cache",
                            "content-type": "application/json;charset=UTF-8;",
                            "sec-ch-ua-mobile": "?0",
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-site"
                        },
                        "referrer": "https://www.schuh.co.uk/",
                        "referrerPolicy": "strict-origin-when-cross-origin",
                        "body": '{"branchName":\""""
                        + location["BranchName"].lower().replace(" ", "-")
                        + r"""\","culture":"en-gb"}',
                        "method": "POST",
                        "mode": "cors",
                        "credentials": "include"
                        })
                        .then(res => res.json())
                        .then(data => done(data))
                        """
                    )
                    break
                except Exception:
                    driver = get_driver(
                        "https://www.schuh.co.uk/stores/", "secondLine", driver=driver
                    )
                    continue

            location_data = location_data["d"]

            location_data = (
                location_data.replace('"', "'")
                .replace("true", "True")
                .replace("false", "False")
                .replace("\\", "")
                .split(",'BranchLocalInfo'")[0]
                .replace("'s", "s")
                + "}"
            )

            location_data = ast.literal_eval(location_data)

            address = (
                location_data["BranchAddress1"] + " " + location_data["BranchAddress2"]
            )

            hours = ""
            for open_key, close_key in hours_key_list:
                day = open_key[:3]
                open_time = (
                    str(location_data[open_key])[:-2]
                    + ":"
                    + str(location_data[open_key])[-2:]
                )
                end_time = (
                    str(location_data[close_key])[:-2]
                    + ":"
                    + str(location_data[close_key])[-2:]
                )

                hours = hours + day + " " + open_time + "-" + end_time + ", "
            hours = hours[:-2]

            state = "<MISSING>"
            location_type = "<MISSING>"

            search.found_location_at(latitude, longitude)

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
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
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
