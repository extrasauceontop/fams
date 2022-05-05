# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests(verify_ssl=False)
    start_url = "https://www.orange.be/nl/shop_locator/shop.json?LCZSG"
    domain = "orange.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    with SgFirefox() as driver:
        for poi in all_locations:
            page_url = f'https://www.orange.be/nl/shops/{poi["slug"]}'
            poi_data = session.get(
                f'https://www.orange.be/nl/shop_locator/shop/{poi["slug"]}.json'
            ).json()
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)
            hoo = loc_dom.xpath('//div[@class="hours-week"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            phone = poi_data["phone"]
            if phone and phone == "./..":
                phone = ""
            street_address = poi["address"]["thoroughfare"]
            if street_address == "-":
                street_address = ""
            zip_code = poi["address"]["postal_code"]
            if zip_code == "-":
                zip_code = ""
            city = poi["address"]["locality"]
            if city == "-":
                city = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state=poi["address"]["region"],
                zip_postal=zip_code,
                country_code=poi["address"]["country"],
                store_number=poi["id"],
                phone=phone,
                location_type=poi["type"],
                latitude=poi["lat"],
                longitude=poi["lng"],
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
