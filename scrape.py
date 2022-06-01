from sgselenium import SgSelenium
from sgselenium import SgChrome
from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
import os
from proxyfier import ProxyProviders
import ssl

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
    session = SgRequests(proxy_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER)

    url = "https://www.extendedstayamerica.com/hotels/"
    with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        browser_headers = SgSelenium.get_default_headers_for(
            the_driver=driver, request_url=url
        )
    response = session.get(url, headers=browser_headers).text
    json_objects = extract_json(response.split("window.esa.hotelsData = ")[1])

    for location in json_objects:
        locator_domain = "extendedstayamerica.com"
        page_url = "https://www.extendedstayamerica.com" + location["urlMap"]
        location_name = location["title"]
        latitude = location["latitude"]
        longitude = location["longitude"]
        city = location["address"]["city"]
        store_number = location["siteId"]
        address = location["address"]["street"]
        state = location["address"]["region"]
        zipp = location["address"]["postalCode"]
        location_type = "<MISSING>"
        hours = "24/7"
        country_code = "US"
        try:
            phone_response = session.get(page_url, headers=browser_headers).text
            phone_soup = bs(phone_response, "html.parser")

            phone = phone_soup.find("span", attrs={"class": "text-white"}).text.strip()

        except Exception:
            with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
                browser_headers = SgSelenium.get_default_headers_for(
                    the_driver=driver, request_url=page_url
                )
            phone_response = session.get(page_url, headers=browser_headers).text
            phone_soup = bs(phone_response, "html.parser")

            phone = phone_soup.find("span", attrs={"class": "text-white"}).text.strip()

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
    try:
        proxy_pass = os.environ["PROXY_PASSWORD"]

    except Exception:
        proxy_pass = "No"

    if proxy_pass == "No":
        raise Exception("Run this with a proxy")

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
