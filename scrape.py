import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests(proxy_country="us", verify_ssl=False)
    domain = "waterworks.com"
    start_url = "https://www.waterworks.com/us_en/storelocation/index/storelist/"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = {"agIds[]": "1"}
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["storesjson"]:
        page_url = "https://www.waterworks.com/us_en/{}".format(
            poi["rewrite_request_path"]
        )
        with SgFirefox(block_third_parties=True) as driver:
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)

        street_address = poi["address"]
        if "@" in street_address:
            street_address = ""
        hoo = loc_dom.xpath(
            '//dt[contains(text(), "Hours")]/following-sibling::dd//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hoo = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["store_name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zipcode"],
            country_code=poi["country_id"],
            store_number=poi["storelocation_id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
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
