# -*- coding: utf-8 -*-
import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    scraped_urls = []
    start_url = "https://www.kumon.ne.jp/enter/search/search.php"
    domain = "kumon.ne.jp"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_pref = dom.xpath('//div[@class="prefSearch"]//li[@class="pref"]/a/@href')
    for p_url in all_pref:
        response = session.get(urljoin(start_url, p_url))
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//section[@id="slctCity"]//li/a/@href')
        for c_url in all_cities:
            response = session.get(urljoin(start_url, c_url))
            dom = etree.HTML(response.text)
            all_sb = dom.xpath('//section[@id="slctCity"]//li/a/@href')
            for sb_url in all_sb:
                lat = re.findall("x=(.+?)&", sb_url)[0]
                lng = re.findall("y=(.+?)&", sb_url)[0]
                post_url = "https://www.kumon.ne.jp/enter/search/classroom_search.php"
                frm = {
                    "age": "noSelect",
                    "open": "noSelect",
                    "searchAddress": "",
                    "online": "noSelect",
                    "cx": lat,
                    "cy": lng,
                    "xmin": str(float(lat) - 300.00),
                    "xmax": str(float(lat) + 300.00),
                    "ymin": str(float(lng) - 300.0),
                    "ymax": str(float(lng) + 300.0),
                    "scaleId": "5",
                    "isscale": "0",
                    "code": "",
                    "search_zip": "",
                }
                data = session.post(post_url, data=frm)
                if data.status_code != 200:
                    continue
                data = data.json()
                for poi in data["classroomList"]:
                    page_url = f"https://www.kumon.ne.jp/enter/search/classroom/{poi['cid']}/index.html".lower()
                    if page_url in scraped_urls:
                        continue
                    scraped_urls.append(page_url)
                    raw_address = poi["addr"] + poi["saddr"]
                    addr = parse_address_intl(raw_address)
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += ", " + addr.street_address_2
                    loc_response = session.get(page_url)
                    if loc_response.status_code != 200:
                        continue
                    loc_dom = etree.HTML(loc_response.text)
                    hoo = loc_dom.xpath('//div[@class="days"]//text()')
                    hoo = " ".join([e.strip() for e in hoo if e.strip()])

                    item = SgRecord(
                        locator_domain=domain,
                        page_url=page_url,
                        location_name=poi["rname"] + "教室",
                        street_address=street_address,
                        city=addr.city,
                        state=addr.state,
                        zip_postal=poi["yubno"],
                        country_code=addr.country,
                        store_number=poi["id"],
                        phone=poi["ktelno"],
                        location_type="",
                        latitude="",
                        longitude="",
                        hours_of_operation=hoo,
                        raw_address=raw_address,
                    )

                    yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
