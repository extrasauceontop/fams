from sgselenium import SgChrome
from proxyfier import ProxyProviders
from bs4 import BeautifulSoup as bs
import ssl
from sgscrape import simple_scraper_pipeline as sp
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    url = "https://www.luckysupermarkets.com/stores/?coordinates=39.64096403685537,-112.39632159999998&zoom=5"
    with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        driver.get(url)
        response = driver.page_source

        soup = bs(response, "html.parser")
        grids = soup.find("div", class_="store-list__scroll-container").find_all("li")
        for grid in grids:
            name = grid.find("span", attrs={"class": "name"}).text.strip()
            number = grid.find("span", attrs={"class": "number"}).text.strip()
            page_url = (
                "https://www.luckysupermarkets.com/stores/"
                + name.split("\n")[0].replace(" ", "-").replace(".", "").lower()
                + "-"
                + number.split("\n")[0].split("#")[-1]
                + "/"
                + grid["id"].split("-")[-1]
            )

            driver.get(page_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "store-details-store-hours__content")
                )
            )

            location_soup = bs(driver.page_source, "html.parser")

            locator_domain = "luckysupermarkets.com"
            location_name = location_soup.find("meta", attrs={"property": "og:title"})[
                "content"
            ]
            address = location_soup.find("meta", attrs={"property": "og:street-address"})[
                "content"
            ]
            city = location_soup.find("meta", attrs={"property": "og:locality"})["content"]
            state = location_soup.find("meta", attrs={"property": "og:region"})["content"]
            zipp = location_soup.find("meta", attrs={"property": "og:postal-code"})["content"]
            country_code = location_soup.find("meta", attrs={"property": "og:country-name"})[
                "content"
            ]
            store_number = location_name.split("#")[-1]
            phone = location_soup.find("meta", attrs={"property": "og:phone_number"})["content"]
            location_type = "<MISSING>"
            latitude = location_soup.find("meta", attrs={"property": "og:location:latitude"})[
                "content"
            ]
            longitude = location_soup.find("meta", attrs={"property": "og:location:longitude"})[
                "content"
            ]

            hours = ""
            days = location_soup.find("dl", attrs={"aria-label": "Store Hours"}).find_all("dt")
            hours_list = location_soup.find("dl", attrs={"aria-label": "Store Hours"}).find_all(
                "dd"
            )

            for x in range(len(days)):
                day = days[x].text.strip()
                hour = hours_list[x].text.strip()
                hours = hours + day + " " + hour + ", "

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
