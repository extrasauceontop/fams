from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context
session = SgRequests()
website = "bathandbodyworks_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.bathandbodyworks.com"
MISSING = SgRecord.MISSING


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


def fetch_data():
    base_url = (
        "https://www.bathandbodyworks.com/north-america/global-locations-canada.html"
    )
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("div", {"class": "store-location"})
    for i in data:
        data2 = i.find("p", {"class": "location"})
        state = data2.text.split(",")[-1].strip()
        city = data2.text.split(",")[0].strip()
        location_name = i.find("p").text
        data3 = i.find("p", {"class": "title"})
        phone = data3.find_next_sibling().text
        log.info(phone)
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=base_url,
            location_name=location_name,
            street_address=MISSING,
            city=city,
            state=state,
            zip_postal=MISSING,
            country_code="CA",
            store_number=MISSING,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=MISSING,
        )
    base_url = "https://www.bathandbodyworks.com"


    url = "https://www.bathandbodyworks.com/on/demandware.store/Sites-BathAndBodyWorks-Site/en_US/Stores-GetNearestStores?latitude=40.7895453&longitude=-74.05652980000002&countryCode=US&distanceUnit=mi&maxdistance=100000&BBW=1"
    with SgChrome(is_headless=False).driver() as driver:
        driver.get(url)
        response = driver.page_source
    
    json_objects = extract_json(response)

    location_data = json_objects[0]["stores"]
    for key in location_data:
        store_data = location_data[key]
        location_name = store_data["name"]
        street_address = store_data["address1"] + " " + store_data["address2"]
        city = store_data["city"]
        state = store_data["stateCode"]
        zip_postal = store_data["postalCode"]
        country_code = store_data["countryCode"]
        phone = store_data["phone"]
        log.info(phone)
        store_number = key
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]
        hours_of_operation = " ".join(
            list(BeautifulSoup(store_data["storeHours"], "lxml").stripped_strings)
        )
        url = "https://www.bathandbodyworks.com/store-locator"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
