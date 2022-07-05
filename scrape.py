from datetime import datetime, timedelta
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from proxyfier import ProxyProviders
from sgselenium import SgChrome
from proxyfier import ProxyProviders
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context


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


def fetch_data(la, ln, sgw: SgWriter):
    url = "https://nomnom-prod-api.pieology.com/restaurants/near?lat=" + str(la) + "&long=" + str(ln) + "&radius=100&limit=500&nomnom=calendars&nomnomcalendar_from=" + calendar_from + "&nomnom_calendars_to=" + calendar_to + "&nomnom_exclude_extref=999"
    driver.get(url)

    js = extract_json(driver.page_source)[0]["restaurants"]

    search.found_nothing()
    for j in js:
        location_name = j.get("name")
        print(location_name)
        street_address = j.get("streetaddress")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        phone = j.get("telephone")
        store_number = j.get("extref")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        if store_number == "Lab":
            continue

        _tmp = []
        try:
            calendar = j["calendars"]["calendar"]
        except KeyError:
            calendar = []

        for cal in calendar:
            _type = cal.get("type") or ""
            if _type == "business":
                days = cal.get("ranges") or []
                for d in days:
                    day = d.get("weekday")
                    start = d.get("start") or ""
                    end = d.get("end") or ""
                    _tmp.append(f"{day}: {start.split()[-1]}-{end.split()[-1]}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    with SgChrome(block_third_parties=False, proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        locator_domain = "https://pieology.com/"

        calendar_from = datetime.today().strftime("%Y%m%d")
        calendar_to = (datetime.today() + timedelta(days=6)).strftime("%Y%m%d")

        with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
            search = DynamicGeoSearch(
                country_codes=[SearchableCountries.USA],
                max_search_distance_miles=200,
                expected_search_radius_miles=100,
                max_search_results=20,
            )

            for lat, lng in search:
                fetch_data(lat, lng, writer)
