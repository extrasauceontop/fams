import json
from urllib.parse import urljoin
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def fetch_data():
    start_url = "https://www.greasemonkeyauto.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=5ca57c5aba&load_all=1&layout=1&category=87%2C86%2C85%2C84%2C83%2C82%2C81%2C80%2C79%2C78%2C77%2C76%2C75%2C74%2C73%2C72%2C71%2C70%2C69%2C68%2C67%2C66%2C65%2C64%2C63%2C62%2C61%2C60%2C58%2C57%2C56%2C55%2C53%2C132%2C140%2C143%2C144"
    domain = "greasemonkeyauto.com"  

    with SgChrome() as driver:
        driver.get(start_url)
        response = driver.page_source

    all_locations = extract_json(response)
    for poi in all_locations:
        page_url = urljoin("https://www.greasemonkeyauto.com/", poi["website"])
        hoo = []
        hoo_data = json.loads(poi["open_hours"])
        for day, hours in hoo_data.items():
            hoo.append(f"{day}: {hours[0]}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"],
            street_address=poi["street"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
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