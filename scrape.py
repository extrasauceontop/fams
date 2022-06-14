from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
import json


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
    page_urls = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        granularity=Grain_8(),
        expected_search_radius_miles=25,
    )
    session = SgRequests()
    url = "https://www.bupa.co.uk/BDC/GoogleMapSearch"

    for search_lat, search_lon in search:
        x = 0
        while True:
            x = x + 1
            params = {
                "latitude": str(search_lat),
                "longitude": str(search_lon),
                "searchFilter": [],
                "dataCount": "1",
                "pageIndex": x,
                "campaignId": None,
            }

            response = session.post(url, json=params)
            try:
                response = response.json()
            except Exception:
                search.found_nothing()
                break
            if len(response) == 0:
                break
            for location in response:
                locator_domain = "www.bupa.co.uk"
                page_url = "https://www.bupa.co.uk" + location["PageUrl"]
                location_name = location["PageTitle"]
                latitude = location["Latitude"]
                longitude = location["Longitude"]
                search.found_location_at(latitude, longitude)
                store_number = "<MISSING>"

                address_parts = location["FullAddress"].split(", ")

                if len(address_parts) == 2:
                    city = "<MISSING>"
                    address = address_parts[0]
                    zipp = address_parts[-1]
                    state = "<MISSING>"
                    country_code = "UK"

                elif len(address_parts) > 2:
                    address = "".join(part + " " for part in address_parts[:-2])
                    city = address_parts[-2]
                    zipp = address_parts[-1]
                    state = "<MISSING>"
                    country_code = "UK"

                location_type = "<MISSING>"

                if page_url in page_urls:
                    continue
                page_urls.append(page_url)
                page_response = session.get(page_url)
                json_objects = extract_json(page_response)

                for item in json_objects:
                    if "openingHoursSpecification" not in item.keys():
                        continue
                    
                    hours = ""
                    for hour_object in item["openingHoursSpecification"]:
                        for day in hour_object["dayOfWeek"]:
                            sta = hour_object["opens"]
                            end = hour_object["closes"]

                            hours = hours + day + " " + sta + "-" + end + ", "
                    
                    hours = hours[:-2]
                    phone = item["telephone"]


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
