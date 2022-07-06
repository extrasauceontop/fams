from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.converse.com.au/allstores"
    domain = "converse.com.au"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="all-stores-list"]//a')
        for l in all_locations:
            location_name = l.xpath("text()")[0]
            if "converse" not in location_name.lower():
                continue
            url = l.xpath("@href")[0]
            store_url = urljoin(start_url, url)
            driver.get(store_url)
            sleep(20)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath('//div[@itemprop="name"]/text()')[0]
            str_1 = loc_dom.xpath('//span[@itemprop="shopNoUnit"]/text()')
            str_1 = str_1[0] if str_1 else ""
            str_2 = loc_dom.xpath('//span[@itemprop="streetNumber"]/text()')
            str_2 = str_2[0] if str_2 else ""
            str_3 = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
            str_3 = str_3[0] if str_3 else ""
            str_4 = loc_dom.xpath('//span[@itemprop="streetType"]/text()')
            str_4 = str_4[0] if str_4 else ""
            street_address = f"{str_1} {str_2} {str_3} {str_4}".strip()
            loc_raw = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[
                0
            ].split(", ")
            hoo = loc_dom.xpath('//div[@class="hours"]//ul//span/text()')
            hoo = " ".join(hoo)
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps/@")]/@href')[0]
                .split("@")[-1]
                .split(",")[:2]
            )
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')[0]
            country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=loc_raw[0],
                state=loc_raw[1],
                zip_postal=loc_raw[2],
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
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
