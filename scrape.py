from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "rocketfizz.com"
    start_url = "https://rocketfizz.com/?sl_engine=sl-xml"

    response = session.get(start_url)
    print(response.text)
    dom = etree.XML(response.text)
    all_locations = dom.xpath("//marker")
    print(len(all_locations))
    x = 0
    for poi_html in all_locations:
        x = x+1
        # if x == 10:
        #     return
        page_url = poi_html.xpath("@url")[0]
        location_name = poi_html.xpath("@name")[0].replace("&#44;", ",")
        street_address = poi_html.xpath("@street")[0].replace("&#44;", ",")
        city = poi_html.xpath("@city")[0]
        state = poi_html.xpath("@state")[0]
        zip_code = poi_html.xpath("@zip")[0]
        phone = poi_html.xpath("@phone")[0].replace("(FIZZ)", "")
        phone = phone.replace("?", "") if phone else ""
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        days = loc_dom.xpath("//table/tbody/tr/td[1]/text()")[1:]
        if not days:
            days = loc_dom.xpath('//td[contains(text(), "Hours:")]/text()')[1:]
        days = [elem.strip() for elem in days]
        hours = loc_dom.xpath("//table/tbody/tr/td[2]/text()")[1:]
        if not hours:
            hours = loc_dom.xpath(
                '//td[contains(text(), "Hours:")]/following-sibling::td/text()'
            )[1:]
        hours = [elem.strip() for elem in hours]
        hours_of_operation = list(map(lambda day, hour: day + " " + hour, days, hours))
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
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
