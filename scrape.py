# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin
from time import sleep
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://api.sallinggroup.com/v2/stores/?brand=br&per_page=200"
    domain = "br.dk"
    hdr = {
        "accept": "application/json, text/plain, */*",
        "authorization": "Bearer 4a368f3b-2d01-4338-bc9f-2b5c7d81d195",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    print(all_locations)
    home_url = "https://www.br.dk/kundeservice/find-din-br/"
    with SgFirefox() as driver:
        driver.get(home_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)
        all_urls = dom.xpath('//div[@class="cta"]/a/@href')
        for url in all_urls:
            page_url = urljoin(home_url, url)
            driver.get(page_url)
            sleep(15)
            loc_dom = etree.HTML(driver.page_source)
            location_name = loc_dom.xpath("//h1/text()")[0]
            for e in all_locations:
                if e["name"] in location_name:
                    poi = e
                    break
            hoo = []
            for e in poi["hours"]:
                if e["closed"]:
                    closes_time = datetime.fromisoformat(str(e["date"]))
                    closes = closes_time.strftime("%A %d %b, %Y")
                    hoo.append(f"{closes} closed")
                else:
                    opens_time = datetime.fromisoformat(str(e["open"]))
                    opens = opens_time.strftime("%A %H:%M")
                    closes_time = datetime.fromisoformat(str(e["close"]))
                    closes = closes_time.strftime("%H:%M")
                    hoo.append(f"{opens} - {closes}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"]["street"],
                city=poi["address"]["city"],
                state="",
                zip_postal=poi["address"]["zip"],
                country_code=poi["address"]["country"],
                store_number=poi["sapSiteId"],
                phone=poi["phoneNumber"],
                location_type="",
                latitude=poi["coordinates"][0],
                longitude=poi["coordinates"][1],
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
