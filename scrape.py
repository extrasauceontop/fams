from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import math
from concurrent.futures import ThreadPoolExecutor
from webdriver_manager.chrome import ChromeDriverManager
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

logger = SgLogSetup().get_logger("quizclothing")
_headers = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://mrbeastburger.com",
    "referer": "https://mrbeastburger.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header2 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mrbeastburger.com"
base_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants?includePrivate=false"
calendar_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants/{}/calendars?from={}&to={}"
today = datetime.today()
mon = (today + timedelta(days=-today.weekday())).strftime("%Y%m%d")
next_mon = (today + timedelta(days=-today.weekday(), weeks=1)).strftime("%Y%m%d")
max_workers = 32


def fetchConcurrentSingle(link):
    page_url = locator_domain + "/locations" + link["url"].split("/menu")[-1]
    logger.info(page_url)
    try:
        ca = request_with_retries(
            calendar_url.format(link["id"], mon, next_mon)
        ).json()["calendar"]
    except:
        ca = None
    return link, page_url, ca


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ) as driver:
        driver.get(base_url)
        locations = bs(driver.page_source, "lxml").select("restaurant")
        for _, page_url, ca in fetchConcurrentList(locations):
            hours = []
            if ca:
                for hr in ca["calendar"]:
                    if not hr["label"]:
                        for hh in hr["ranges"]:
                            temp = f"{hh['weekday']}: {hh['start'].split()[-1]} - {hh['end'].split()[-1]}"
                            if temp not in hours:
                                hours.append(temp)
                        break
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["streetaddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
