from datetime import datetime, timedelta
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data(la, ln, sgw: SgWriter):
    params = (
        ("lat", str(la)),
        ("long", str(ln)),
        ("radius", "100"),
        ("limit", "500"),
        ("nomnom", "calendars"),
        ("nomnom_calendars_from", calendar_from),
        ("nomnom_calendars_to", calendar_to),
        ("nomnom_exclude_extref", "999"),
    )

    r = session.get(api, headers=headers, params=params)
    js = r.json()["restaurants"]

    for j in js:
        location_name = j.get("name")
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
    session = SgRequests()
    locator_domain = "https://pieology.com/"
    api = "https://nomnom-prod-api.pieology.com/restaurants/near"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    }
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
