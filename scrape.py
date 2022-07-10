from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from proxyfier import ProxyProviders


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self.__http = http  # noqa
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,  # noqa
        current_country: str,
        items_remaining: int,  # noqa
        found_location_at: Callable[[float, float], None],
        found_nothing: Callable[[], None],
    ) -> Iterable[SgRecord]:  # noqa
        
        domain = "zara.com"
        search_lat = coord[0]
        search_lon = coord[1]

        url = "https://www.zara.com/{}/en/stores-locator/search?lat={}&lng={}&isGlobalSearch=false&showOnlyPickup=false&isDonationOnly=false&ajax=true".format(
            current_country, search_lat, search_lon
        )
        all_locations = http.get(url, headers=hdr)
        print(all_locations)

        all_locations = all_locations.json()
        if not all_locations:
            found_nothing()
        for poi in all_locations:
            street_address = poi["addressLines"][0]
            location_name = poi.get("name")
            if not location_name:
                location_name = street_address
            state = poi.get("state")
            if state == "--":
                state = ""
            if state and state.isdigit():
                state = ""
            zip_code = poi["zipCode"]
            if zip_code and str(zip_code.strip()) == "0":
                zip_code = ""
            phone = poi["phones"]
            phone = phone[0] if phone else ""
            if phone == "--":
                phone = ""

            found_location_at(poi["latitude"], poi["longitude"])

            rec_count = self.__state.get_misc_value(
                current_country, default_factory=lambda: 0
            )
            self.__state.set_misc_value(current_country, rec_count + 1)

            yield SgRecord(
                raw={
                    "locator_domain": domain,
                    "page_url": f"https://www.zara.com/{current_country}/en/z-stores-st1404.html?v1=11108",
                    "location_name": location_name,
                    "latitude": poi["latitude"],
                    "longitude": poi["longitude"],
                    "city": poi["city"],
                    "store_number": poi["id"],
                    "street_address": street_address,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "location_type": poi["datatype"],
                    "hours": "<MISSING>",
                    "country_code": poi["countryCode"],
                }
            )

if __name__ == "__main__":
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_4()
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        with SgRequests(proxy_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[
                    SearchableCountries.THAILAND
                ],
            )
            #    max_threads=8)

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()