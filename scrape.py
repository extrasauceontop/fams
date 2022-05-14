from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgFirefox
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data():
    start_url = "https://burtonsgrill.com/locations/"
    domain = "burtonsgrill.com"

    with SgFirefox() as driver:
        driver.get_and_wait_for_request(start_url)

        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="locations-group"]//a/@href')
        for page_url in all_locations:
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath('//h1[@class="title h3"]/text()')
            location_name = location_name[0] if location_name else ""
            raw_address = loc_dom.xpath('//a[contains(@href, "maps")]/text()')
            if not raw_address:
                all_locations += loc_dom.xpath(
                    '//div[@class="locations-group"]//a/@href'
                )
                continue
            raw_address = raw_address[0].split(", ")
            street_address = raw_address[0]
            addr = parse_address_intl(" ".join(raw_address))
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]
            hoo = loc_dom.xpath(
                '//div[i[@class="icon-clock"]]/following-sibling::div[1]//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""
            if hours_of_operation and "Coming Soon" in hours_of_operation:
                continue

            city = addr.city
            state = addr.state
            zipp = addr.postcode

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(raw_address),
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