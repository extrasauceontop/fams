import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from sgselenium import SgFirefox
import time

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data():
    with SgFirefox(is_headless=True) as driver:
        url = "https://example.com/"
        driver.get(url)
        time.sleep(10)
        statelist = [
            "ab",
            "BC",
            "MB",
            "NB",
            "NL",
            "NT",
            "NS",
            "NU",
            "ON",
            "PE",
            "QC",
            "SK",
            "YT",
        ]
        for st in statelist:
            url = (
                "https://www.atriaretirement.ca/wp-content/themes/aslblanktheme/script-getstatelocations.php?state="
                + st
            )

            driver.get(url)
            loclist = driver.page_source.split('"communities":', 1)[1].split("]}<", 1)[0]
            loclist = loclist + "]"
            loclist = json.loads(loclist)
            for loc in loclist:

                store = loc["community_number"]
                title = loc["name"]
                street = loc["address_1"] + loc["address_2"]
                city = loc["city"]
                state = loc["province"]
                pcode = loc["postal_code"]
                phone = loc["phone"]
                lat = loc["latitude"]
                longt = loc["longitude"]
                link = loc["url"]

                yield SgRecord(
                    locator_domain="https://www.atriaretirement.ca/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="CA",
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=SgRecord.MISSING,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
