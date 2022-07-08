from sgselenium import SgFirefox
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgscrape import simple_scraper_pipeline as sp
import time


def get_data():
    url = "https://www.galeria.de/filialen/l"
    x = 0
    with SgFirefox(is_headless=False ) as driver:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ubsf_message"))
        )
        response = driver.page_source

        soup = bs(response, "html.parser")
        region_links = [a_tag["href"] for a_tag in soup.find_all("a", attrs={"class": "ubsf_sitemap-group-link"})]

        for region_link in region_links:
            driver.get(region_link)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ubsf_sitemap-location-name"))
            )
            region_response = driver.page_source
            region_soup = bs(region_response, "html.parser")
            page_urls = [div_tag.find("a")["href"] for div_tag in region_soup.find_all("div", attrs={"class": "ubsf_sitemap-location-name"})]
            for page_url in page_urls:
                x = x+1
                if x == 10:
                    return
                driver.get(page_url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ubsf_details-details-title"))
                )
                time.sleep(10)
                page_response = driver.page_source
                page_soup = bs(page_response, "html.parser")

                locator_domain = "www.galeria.de"
                location_name = page_soup.find("h1", attrs={"class": "ubsf_details-details-title"}).text.strip()

                latitude = page_response.split('latitude":')[1].split(",")[0]
                longitude = page_response.split('longitude":')[1].split("}")[0]
                
                address_parts = page_soup.find("address", attrs={"class": "ubsf_details-address"}).text.strip()

                address = address_parts.split(", ")[0]
                zipp = address_parts.split(", ")[1].split(" ")[0]
                city = "".join(part + " " for part in address_parts.split(", ")[1].split(" ")[1:])
                state = "<MISSING>"
                country_code = "DE"
                location_type = "<MISSING>"
                phone = page_soup.find("li", attrs={"class": "ubsf_details-phone"}).text.strip().replace("+", "")
                store_number = "<MISSING>"
                
                hours = ""
                hours_parts = page_soup.find("div", attrs={"class": "ubsf_location-page-opening-hours-list"}).find_all("div", attrs={"class": "ubsf_opening-hours-day"})

                for part in hours_parts:
                    day = part.find("div", attrs={"class": "ubsf_left-side"}).text.strip()
                    times = part.find("div", attrs={"class": "ubsf_right-side"}).text.strip().replace("geschlossen", "")
                    if len(times) < 5:
                        times = "geschlossen"

                    hours = hours + day + " " + times + ", "
                
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
# <div class="ubsf_sitemap-location-name"><a href="https://www.galeria.de/filialen/l/aachen/adalbertstrasse-20-30/001439">GALERIA Aachen</a></div>