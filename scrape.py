import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.rewe.de/market/content/marketsearch"

    for i in range(100):
        data = f'-----------------------------335590349241424249481678125346\r\nContent-Disposition: form-data; name="searchString"\r\n\r\n*\r\n-----------------------------335590349241424249481678125346\r\nContent-Disposition: form-data; name="page"\r\n\r\n{i}\r\n-----------------------------335590349241424249481678125346\r\nContent-Disposition: form-data; name="city"\r\n\r\n\r\n-----------------------------335590349241424249481678125346\r\nContent-Disposition: form-data; name="pageSize"\r\n\r\n50\r\n-----------------------------335590349241424249481678125346--\r\n'
        r = session.post(api, headers=headers, data=data)
        try:
            js = r.json()["markets"]
            broken = False
        except:
            broken = True
            js = json.loads(r.text + "}}]}")["markets"]

        for j in js:
            a = j.get("address") or {}
            street_address = a.get("street")
            city = a.get("city")
            state = a.get("state")
            postal = a.get("postalCode")
            country_code = "DE"
            store_number = j.get("id")
            location_name = j.get("headline")
            page_url = f"https://www.rewe.de/marktseite/?wwident={store_number}"
            phone = j.get("phone")

            g = j.get("geoLocation") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            _tmp = []
            try:
                hours = j["openingHours"]["condensed"]
            except:
                hours = []

            for h in hours:
                day = h.get("days")
                inter = h.get("hours")
                _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 50 and not broken:
            break


if __name__ == "__main__":
    locator_domain = "https://www.rewe.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.rewe.de/marktsuche/",
        "Content-Type": "multipart/form-data; boundary=---------------------------335590349241424249481678125346",
        "Origin": "https://www.rewe.de",
        "Alt-Used": "www.rewe.de",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
