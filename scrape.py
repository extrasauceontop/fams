# -*- coding: utf-8 -*-
from time import sleep
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
# from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.adecco.no/kontakt-oss/"
    domain = "adecco.no"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="row text-left"]//a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[-1]
        geo = (
            loc_dom.xpath('//iframe[@id="mapFrame"]/@src')[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath(
            '//p[contains(text(), "Åpningstider:")]/following-sibling::p//text()'
        )[0].replace("g0", "g 0")

        x = 0
        while True:
            x = x+1
            if x == 10:
                print(loc_dom)
                raise Exception
            try:
                with SgFirefox() as driver:
                    driver.get(page_url)
                    sleep(5)
                    driver.switch_to.frame(driver.find_element_by_id("mapFrame"))
                    loc_dom = etree.HTML(driver.page_source)
                raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0]
                break

            except Exception:
                continue
        
        # addr = parse_address_intl(raw_address)
        # street_address = addr.street_address_1
        # if addr.street_address_2:
        #     street_address += " " + addr.street_address_2
        street_address = "<LATER>"
        city = "<LATER>"
        zipp = "<LATER>"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zipp,
            country_code="NO",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
