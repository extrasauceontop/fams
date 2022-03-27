from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration


def record_transformer(poi):
    domain = "zara.com"
    street_address = poi["addressLines"][0]
    location_name = poi.get("name")
    if not location_name:
        location_name = street_address
    city = poi["city"]
    city = city if city else ""
    state = poi.get("state")
    state = state if state else ""
    if state == "--":
        state = SgRecord.MISSING
    if state.isdigit():
        state = ""
    zip_code = poi["zipCode"]
    zip_code = zip_code if zip_code else ""
    if zip_code and str(zip_code.strip()) == "0":
        zip_code = ""
    country_code = poi["countryCode"]
    store_number = poi["id"]
    phone = poi["phones"]
    phone = phone[0] if phone else ""
    if phone == "--":
        phone = SgRecord.MISSING
    location_type = poi["datatype"]
    latitude = poi["latitude"]
    latitude = latitude if latitude else ""
    longitude = poi["longitude"]
    longitude = longitude if longitude else ""

    item = SgRecord(
        locator_domain=domain,
        page_url=SgRecord.MISSING,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_code,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=SgRecord.MISSING,
    )
    return (item, latitude, longitude)


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self.__http = http  # noqa
        self.__state = CrawlStateSingleton.get_instance()  # noqa

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,  # noqa
        current_country: str,
        items_remaining: int,  # noqa
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        hdr = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
        }

        def getPoint(session, hdr):
            url = "https://www.zara.com/{}/en/stores-locator/search?lat={}&lng={}&isGlobalSearch=true&showOnlyPickup=false&isDonationOnly=false&ajax=true".format(
                current_country, coord[0], coord[1]
            )
            data = session.get(url, headers=hdr)
            try:
                return data.json()
            except Exception:
                return []

        found = 0
        for poi in getPoint(http, hdr):
            record, foundLat, foundLng = record_transformer(poi)
            found_location_at(foundLat, foundLng)
            found += 1
            yield record


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_8()
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=[403, 429, 500, 502, 404]) as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
            )

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
