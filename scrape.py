from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import time


def get_data():
    session = SgRequests()
    start_url = "https://www.munichsports.com/en/munich-stores"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    response = session.get(start_url, headers=headers).text.replace("<br>", "\n")
    soup = bs(response, "html.parser")

    grids = soup.find_all("div", attrs={"class": "shop-text text-center"})

    for location in grids:
        time.sleep(1)
        locator_domain = "https://www.munichsports.com"
        page_url = (
            locator_domain
            + location.find("div", attrs={"class": "shop-name"}).find("a")["href"]
        )
        location_name = (
            location.find("div", attrs={"class": "shop-name"})
            .find("span", attrs={"class": "store"})
            .text.strip()
        )
        city = location.find("span", attrs={"class": "city"}).text.strip()
        store_number = "<MISSING>"
        address = (
            location.find("div", attrs={"class": "shop-address"})
            .text.strip()
            .split("\n")[0]
            .replace("C.C. ", "")
            .replace("C/ ", "")
        )
        state = "<MISSING>"
        zipp = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "ES"

        if page_url == "https://www.munichsports.com/en/pages/191":
            phone = "<MISSING>"
            page_url = "<MISSING>"
            hours = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            pass

        else:
            location_response = session.get(page_url, headers=headers).text
            location_soup = bs(location_response, "html.parser")

            try:
                phone = (
                    location_soup.find("div", attrs={"class": "store-phone store-txt"})
                    .find("a")["href"]
                    .replace("tel:", "")
                    .replace("+", "")
                )
            except Exception:
                phone_part = location_soup.find(
                    "div", attrs={"class": "store-phone store-txt"}
                ).text.strip()

                phone = ""
                for character in phone_part:
                    if character.isdigit():
                        phone = phone + character

            lat_lon_part = location_soup.find(
                "iframe", attrs={"class": "embed-responsive-item"}
            )["src"]
            latitude = lat_lon_part.split("!3d")[1].split("!")[0]
            longitude = lat_lon_part.split("!2d")[1].split("!3d")[0]

            hours = location_soup.find(
                "div", attrs={"class": "store-time store-txt"}
            ).text.strip()

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
