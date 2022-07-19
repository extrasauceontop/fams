from requests_toolbelt import MultipartEncoder
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.columbia.hu/?ajax_event=load_shop_finder_data"
    domain = "columbia.hu"

    frm = {"ajax_event": "load_shop_finder_data"}
    me = MultipartEncoder(fields=frm)
    me_boundary = me.boundary[2:]
    me_body = me.to_string()
    hdr = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "multipart/form-data; boundary=" + me_boundary,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = session.post(start_url, data=me_body, headers=hdr).json()
    for poi in data["shops"]:
        page_url = urljoin(start_url, poi["url"])
        raw_address = poi["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = " ".join(poi["open"].split()).replace("$", " ").replace("|", " ")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["label"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=raw_address.split()[0],
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["gps"].split(",")[0],
            longitude=poi["gps"].split(",")[1],
            hours_of_operation=hoo,
            raw_address=poi["address"],
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
