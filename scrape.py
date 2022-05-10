from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    url = "https://www.simons.ca/en/stores/our-stores--a13090"

    with SgChrome(
        user_agent=user_agent,
        is_headless=True,
    ).driver() as driver:
        driver.get(url)

        response = driver.page_source
        soup = bs(response, "html.parser")

        a_tags = soup.find_all(
            "a",
            attrs={
                "class": "simonsLandingStoreCardLink",
            },
        )
        class_name = "stores-title"
        for a_tag in a_tags:
            locator_domain = "simons.ca"
            page_url = a_tag["href"]

            driver.get(page_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            location_response = driver.page_source
            location_soup = bs(location_response.replace("<br>", "\n"), "html.parser")

            location_name = location_soup.find(
                "h1",
                attrs={
                    "class": "stores-title",
                },
            ).text.strip()

            lat_lon_parts = location_soup.find(
                "a",
                attrs={
                    "class": "stores-mapLink",
                },
            )["href"]
            try:
                latitude = lat_lon_parts.split("@")[1].split(",")[0]
                longitude = lat_lon_parts.split("@")[1].split(",")[1]
            except Exception:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            address_parts = (
                location_soup.find(
                    "p",
                    attrs={
                        "class": "stores-address",
                    },
                )
                .text.strip()
                .split("\n")
            )

            city = address_parts[-1].split(", ")[0]
            store_number = "<MISSING>"
            address = address_parts[0]
            state = address_parts[-1].split(", ")[1].split(" ")[0]
            zipp = "".join(
                part + " " for part in address_parts[-1].split(", ")[1].split(" ")[1:]
            )

            phone = location_soup.find("a", attrs={"class": "stores-tel"})[
                "href"
            ].replace("tel:", "")
            location_type = "<MISSING>"
            country_code = "CA"

            days = location_soup.find(
                "div",
                attrs={
                    "class": "stores-hoursLeft",
                },
            ).find_all("p")
            hours_parts = location_soup.find(
                "div", attrs={"class": "stores-hoursRight"}
            ).find_all("p")

            hours = ""
            for x in range(len(days)):
                day = days[x].text.strip()
                part = hours_parts[x].text.strip()

                hours = hours + day + " " + part + ", "

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
