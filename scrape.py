from sgselenium import SgFirefox
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import json
import ssl
from sglogging import sglog
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest
import re
import unidecode

ssl._create_default_https_context = ssl._create_unverified_context
crawl_state = CrawlStateSingleton.get_instance()
log = sglog.SgLogSetup().get_logger(logger_name="carrefour")


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

                if "stores" in html_string[start : end + 1]:
                    try:
                        json_objects.append(json.loads(html_string[start : end + 1]))
                    except Exception:
                        pass
        count = count + 1

    return json_objects


def get_urls():
    url = "https://www.carrefour.fr/magasin"
    with SgFirefox(
        block_third_parties=True,
        proxy_country="fr",
    ) as driver:
        driver.get(url)
        response = driver.page_source
        soup = bs(response, "html.parser")
        region_urls = [
            "https://www.carrefour.fr" + li_tag.find("a")["href"]
            for li_tag in soup.find_all(
                "li", attrs={"class": "store-locator-footer-list__item"}
            )
        ]
        for url in region_urls:
            log.info("url: " + url)
            driver.get(url)
            response = driver.page_source
            soup = bs(response, "html.parser")

            subregion_urls = [
                "https://www.carrefour.fr" + li_tag.find("a")["href"]
                for li_tag in soup.find_all(
                    "li", attrs={"class": "store-locator-footer-list__item"}
                )
            ]

            for sub_url in subregion_urls:
                try:
                    driver.get(sub_url)
                    response = driver.page_source
                    json_objects = extract_json(response)
                    json_objects[1]["search"]["data"]["stores"]
                except Exception:
                    driver.get(sub_url)
                    response = driver.page_source
                    json_objects = extract_json(response)

                for location in json_objects[1]["search"]["data"]["stores"]:
                    page_url = "https://www.carrefour.fr" + location["storePageUrl"]
                    if (
                        page_url
                        == "https://www.carrefour.fr/magasin/market-bourgoin-jallieu-rivet"
                    ):
                        continue

                    location_name = location["name"]
                    latitude = location["coordinates"][1]
                    longitude = location["coordinates"][0]
                    city = location["address"]["city"]
                    store_number = location["storeId"]
                    address = location["address"]["address1"].strip()
                    zipp = location["address"]["postalCode"]
                    location_type = location["banner"]

                    if re.search(r"\d", zipp) is False:
                        hold = city
                        city = zipp
                        zipp = hold

                    url_to_save = (
                        page_url
                        + "?location_name="
                        + str(location_name)
                        + "&==latitude="
                        + str(latitude)
                        + "&==longitude="
                        + str(longitude)
                        + "&==city="
                        + str(city)
                        + "&==store_number="
                        + str(store_number)
                        + "&==address="
                        + str(address)
                        + "&==zipp="
                        + str(zipp)
                        + "&==location_type="
                        + str(location_type)
                    )
                    url_to_save = unidecode.unidecode(url_to_save)
                    log.info(url_to_save)
                    crawl_state.push_request(SerializableRequest(url=url_to_save))

    crawl_state.set_misc_value("got_urls", True)


def get_data():
    try:
        with SgFirefox(
            block_third_parties=True,
            proxy_country="fr",
        ) as driver:
            for page_url_thing in crawl_state.request_stack_iter():
                page_url = page_url_thing.url.split("?")[0]
                locator_domain = "carrefour.fr"

                location_deets = page_url_thing.url.split("?")[1]

                location_name = location_deets.split("location_name=")[1].split("&==")[
                    0
                ]
                latitude = location_deets.split("latitude=")[1].split("&==")[0]
                longitude = location_deets.split("longitude=")[1].split("&==")[0]
                city = location_deets.split("city=")[1].split("&==")[0]
                store_number = location_deets.split("store_number=")[1].split("&==")[0]
                address = location_deets.split("address=")[1].split("&==")[0]

                try:
                    if address[-1] == "0":
                        address = address[:-2]
                except Exception:
                    address = "<MISSING>"

                state = "<MISSING>"
                zipp = location_deets.split("zipp=")[1].split("&==")[0]

                log.info("page_url: " + page_url)

                driver.get(page_url)
                phone_response = driver.page_source

                phone_soup = bs(phone_response, "html.parser")
                a_tags = phone_soup.find_all("a")

                phone = "<MISSING>"
                for a_tag in a_tags:
                    if "tel:" in a_tag["href"]:
                        phone = a_tag["href"].replace("tel:", "")
                        break

                location_type = location_deets.split("location_type=")[1].split("&==")[
                    0
                ]
                country_code = "France"

                if page_url != "https://www.carrefour.fr/magasin/":
                    hours_parts = phone_soup.find_all(
                        "li", attrs={"class": "store-page-hours__item"}
                    )
                    hours = ""

                    try:
                        for part in hours_parts:
                            day = part.find(
                                "div", attrs={"class": "store-page-hours__label"}
                            ).text.strip()
                            times = part.find(
                                "div", attrs={"class": "store-page-hours__slice"}
                            ).text.strip()

                            hours = hours + day + " " + times + ", "

                    except Exception:
                        hours = hours + day + " closed, "

                    hours = hours[:-2]
                    hours = hours.replace("à", "-")

                else:
                    hours = "<MISSING>"
                log.info(location_name)
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

    except Exception as e:
        log.info(e)
        crawl_state.push_request(SerializableRequest(url=page_url_thing.url))
        raise Exception


def scrape():
    if not crawl_state.get_misc_value("got_urls"):
        get_urls()

    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
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


x = 0
while True:
    x = x + 1
    if x == 5:
        raise Exception("Check errors")
    try:
        scrape()
        break

    except Exception:
        continue
