import os
import ssl
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-ru:{}@proxy.apify.com:8000/"

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.okmarket.ru"
    api_url = "https://www.okmarket.ru/stores/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    print(r.status_code)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "JSON.parse")]/text()'))
        .split('cityList":')[1]
        .split(',"lang"')[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:
        ids = j.get("id")
        city = j.get("name")

        r = session.get(
            f"https://www.okmarket.ru/ajax/map_filter/search/?lang=ru&city_id={ids}&type=shop",
            headers=headers,
        )
        js = r.json()["data"]["shops"]
        for j in js:

            page_url = f"https://www.okmarket.ru{j.get('url')}"
            location_name = j.get("name")
            street_address = (
                "".join(j.get("address"))
                .replace("\r\n", " ")
                .replace("\n", " ")
                .strip()
            )
            country_code = "RU"
            latitude = j.get("coords").get("latitude")
            longitude = j.get("coords").get("longitude")
            try:
                phone = j.get("phone")[0].get("label")
            except:
                phone = "<MISSING>"
            hours_of_operation = j.get("time").get("label")

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
