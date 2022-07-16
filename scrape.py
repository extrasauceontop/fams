from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgpostal.sgpostal import parse_address_intl


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
        search_lat = coord[0]
        search_lon = coord[1]
        base_link = "https://30b4npq9r7.execute-api.us-east-1.amazonaws.com/api/geolocations"

        json = {"cords": {"lat": str(search_lat), "long": str(search_lon)}, "brand": "Dollar", "radius": 10000}
        try:
            stores = http.post(base_link, headers=hdr, json=json).json()["data"]
        except Exception:
            stores=[]

        for store in stores:
            location_name = store["name"]
            raw_address = store["fullAddress"]
            addr = parse_address_intl(raw_address)
            try:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            except:
                street_address = addr.street_address_1
            if not street_address:
                street_address = raw_address.split(",")[0]
            if len(street_address) < 4:
                street_address = raw_address.split(",")[0]
            city = store["city"]
            fin_city = city.split(",")[0].split("(")[0].strip()
            try:
                if city.lower() in street_address[-len(city) - 1 :].lower():
                    street_address = street_address[: -len(city)].strip()
            except:
                pass
            try:
                link_state = store["state"]
                state = link_state
            except:
                link_state = ""
                state = addr.state
            zip_code = addr.postcode
            try:
                country_code = store["country"]
            except:
                country_code = ""
            store_number = store["location_id"]
            location_type = ""
            try:
                phone = store["phoneNumber"]["number"]
                if len(phone) < 3:
                    phone = ""
            except:
                phone = ""
            hours_of_operation = "<INACCESSIBLE>"
            latitude = store["coords"]["lat"]
            longitude = store["coords"]["long"]
            found_location_at(latitude, longitude)
            link_id = store["oag"].lower()
            if link_state:
                link = f'https://www.dollar.com/location/{country_code}/{state.replace(" ", "").lower()}/{city.replace(" ", "").lower()}/{link_id}'
            else:
                link = f'https://www.dollar.com/location/{country_code}/{city.replace(" ", "").lower()}/{link_id}'

            try:
                country_code = (
                    country_code.replace("southafrica", "south africa")
                    .replace("czechrepublic", "czech republic")
                    .replace("unitedkingdom", "united kingdom")
                    .replace("saintbarthélemy", "saint barthélemy")
                    .replace("unitedstates", "united states")
                    .replace("frenchguiana", "french guiana")
                    .replace("costarica", "costa rica")
                    .replace("caymanislands", "cayman islands")
                    .replace("bosniaandherzegovina", "bosnia and herzegovina")
                    .replace("taiwan,provinceofchina", "taiwan")
                    .replace("bruneidarussalam", "brunei darussalam")
                    .replace("antiguaandbarbuda", "antigua and barbuda")
                    .replace("dominicanrepublic", "dominican republic")
                    .replace("unitedarabemirates", "united arab emirates")
                )
            except:
                pass

            yield SgRecord(
                raw={
                    "locator_domain": "dollar.com",
                    "page_url": link,
                    "location_name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": fin_city,
                    "store_number": store_number,
                    "street_address": street_address,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "location_type": location_type,
                    "hours": hours_of_operation,
                    "country_code": country_code,
                }
            )
        if len(stores) == 0:
            found_nothing()


if __name__ == "__main__":
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", expected_search_radius_miles=500
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        with SgRequests() as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
            )
            #    max_threads=8)

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()