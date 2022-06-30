import ssl
import time

import undetected_chromedriver as uc

from bs4 import BeautifulSoup
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

log = sglog.SgLogSetup().get_logger(logger_name="brookshires.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.brookshires.com/stores/?coordinates=39.84686380709379,-106.87749199999999&zoom=6"

    options = uc.ChromeOptions()
    options.headless = True

    with uc.Chrome(
        driver_executable_path=ChromeDriverManager().install(), options=options
    ) as driver:
        for i in range(10):
            log.info(f"Loading main page {base_link}")
            driver.get(base_link)
            try:
                WebDriverWait(driver, 120).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "store-list__scroll-container")
                    )
                )
                time.sleep(10)
                soup = BeautifulSoup(driver.page_source, "lxml")
                grids = soup.find(
                    "div", class_="store-list__scroll-container"
                ).find_all("li")
                if grids:
                    log.info("Got Grids")
                    break
            except:
                pass

        for grid in grids:
            name = grid.find("span", {"class": "store-name"}).text.strip()
            number = grid.find(
                "span",
                attrs={"ng-if": "$ctrl.showStoreNumber && $ctrl.store.storeNumber"},
            ).text.strip()
            page_url = (
                "https://www.brookshires.com/stores/"
                + name.split("\n")[0].replace(" ", "-").replace(".", "").lower()
                + "-"
                + number.split("\n")[0].split("#")[-1]
                + "/"
                + grid["id"].split("-")[-1]
            )
            time.sleep(2)
            for i in range(10):
                driver.get(page_url)
                log.info("Pull content => " + page_url)
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "store-details-store-hours__content")
                        )
                    )
                    break
                except:
                    time.sleep(10)

            location_soup = BeautifulSoup(driver.page_source, "lxml")

            locator_domain = "https://www.brookshires.com/"
            location_name = location_soup.find("meta", attrs={"property": "og:title"})[
                "content"
            ]
            street_address = location_soup.find(
                "meta", attrs={"property": "og:street-address"}
            )["content"]
            city = location_soup.find("meta", attrs={"property": "og:locality"})[
                "content"
            ]
            state = location_soup.find("meta", attrs={"property": "og:region"})[
                "content"
            ]
            zip = location_soup.find("meta", attrs={"property": "og:postal-code"})[
                "content"
            ]
            country_code = location_soup.find(
                "meta", attrs={"property": "og:country-name"}
            )["content"]
            store_number = location_name.split("#")[-1]
            phone = location_soup.find("meta", attrs={"property": "og:phone_number"})
            if not phone:
                phone = "<MISSING>"
            else:
                phone = phone["content"]
            location_type = "<MISSING>"
            latitude = location_soup.find(
                "meta", attrs={"property": "og:location:latitude"}
            )["content"]
            longitude = location_soup.find(
                "meta", attrs={"property": "og:location:longitude"}
            )["content"]

            hours = ""
            days = location_soup.find(
                "dl", attrs={"aria-label": "Store Hours"}
            ).find_all("dt")
            hours_list = location_soup.find(
                "dl", attrs={"aria-label": "Store Hours"}
            ).find_all("dd")

            for x in range(len(days)):
                day = days[x].text.strip()
                hour = hours_list[x].text.strip()
                hours = hours + day + " " + hour + ", "

            hours_of_operation = hours[:-2]

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
