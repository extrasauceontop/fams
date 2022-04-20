from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from lxml import etree
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest

crawl_state = CrawlStateSingleton.get_instance()


def create_coords():
    left = 446685
    right = 524883

    top = 164000
    bottom = 87605
    
    increment = 750

    x = left
    while x < right:
        y = bottom
        while y < top:
            coord_pair = str(x) + "," + str(y)
            crawl_state.push_request(SerializableRequest(url=coord_pair))
            y = y+increment
        x = x+increment
    
    crawl_state.set_misc_value("got_urls", True)


def get_data():
    page_urls = []
    domain = "kumon.ne.jp"
    search = crawl_state.request_stack_iter()

    session = SgRequests()
    post_url = "https://www.kumon.ne.jp/enter/search/classroom_search.php"

    count = 0
    for coord_pair in search:
        text = coord_pair.url
        search_x = text.split(",")[0]
        search_y = text.split(",")[1]
        count = count + 1
        print(count)
        if count == 100:
            break

        frm = {
            "age": "noSelect",
            "open": "noSelect",
            "searchAddress": "",
            "online": "noSelect",
            "cx": search_x,
            "cy": search_y,
            "xmin": str(float(search_x) - 1000000.00),
            "xmax": str(float(search_y) + 1000000.00),
            "ymin": str(float(search_x) - 1000000.0),
            "ymax": str(float(search_y) + 1000000.0),
            "scaleId": "5",
            "isscale": "0",
            "code": "",
            "search_zip": "",
        }

        data = session.post(post_url, data=frm)
        if data.status_code != 200:
            continue
        data = data.json()
        print(len(data["classroomList"]))
        for poi in data["classroomList"]:
            page_url = f"https://www.kumon.ne.jp/enter/search/classroom/{poi['cid']}/index.html".lower()
            if page_url in page_urls:
                continue
            page_urls.append(page_url)
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
    if not crawl_state.get_misc_value("got_urls"):
        create_coords()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PAGE_URL}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in get_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()