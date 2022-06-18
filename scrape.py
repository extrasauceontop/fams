import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "dillards.com"
    start_url = "https://www.dillards.com/stores"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    print(response.text)
    print(response.status_code)
    dom = etree.HTML(response.text)

    all_poi_urls = dom.xpath('//div[@id="storeListing"]//a[@class="underline"]/@href')
    for url in all_poi_urls:
        page_url = "https://www.dillards.com" + url
        store_response = session.get(page_url)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath('//div[@id="storeDetails"]/script/text()')[0]
        store_data = json.loads(store_data)

        location_name = store_data["name"]
        street_address = store_data["address"]["streetAddress"]
        city = store_data["address"]["addressLocality"]
        state = store_data["address"]["addressRegion"]
        zip_code = store_data["address"]["postalCode"]
        store_number = store_data["url"].split("/")[-1]
        phone = store_data["telephone"]
        location_type = store_data["@type"]

        geo_data = store_dom.xpath(
            '//script[contains(text(), "__INITIAL_STATE__")]/text()'
        )[0]
        geo_data = re.findall("__INITIAL_STATE__ =(.+);", geo_data)[0]
        geo_data = json.loads(geo_data)
        latitude = geo_data["contentData"]["store"]["latitude"]
        longitude = geo_data["contentData"]["store"]["longitude"]
        hoo = []
        for elem in store_data["openingHoursSpecification"]:
            day = elem["dayOfWeek"]["name"]
            opens = elem["opens"]
            closes = elem["closes"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = ", ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
