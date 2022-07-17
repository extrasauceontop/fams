import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
from proxyfier import ProxyProviders


def fetch_data(sgw: SgWriter):
    def check_response(response): # noqa
        try:
            a = driver.page_source
            tree = html.fromstring(a)
            js_block = "".join(tree.xpath('//div[@id="json"]/text()'))
            json.loads(js_block)
            return True
        
        except Exception:
            return False


    locator_domain = "https://www.k-ruoka.fi/"
    api_url = "https://www.k-ruoka.fi/kr-api/stores?offset=0&limit=-1"
    with SgChrome(
        proxy_country="FI",
        proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER,
        response_successful=check_response
    ) as driver:
        driver.get(api_url)
        a = driver.page_source
        tree = html.fromstring(a)
        js_block = "".join(tree.xpath('//div[@id="json"]/text()'))
        js = json.loads(js_block)

        x = 0
        for j in js["results"]:
            x = x+1
            if x == 10:
                return
            slug = j.get("slug")
            page_url = f"https://www.k-ruoka.fi/kauppa/{slug}"
            location_name = j.get("name") or "<MISSING>"
            store_number = j.get("id") or "<MISSING>"
            latitude = j.get("geo").get("latitude") or "<MISSING>"
            longitude = j.get("geo").get("longitude") or "<MISSING>"
            country_code = "FI"
            print(page_url)
            driver.get(page_url)
            a = driver.page_source
            tree = html.fromstring(a)
            js_block = "".join(
                tree.xpath('//script[@type="application/ld+json"]/text()')
            )
            js = json.loads(js_block)
            a = js.get("address")
            street_address = a.get("streetAddress") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            city = a.get("addressLocality") or "<MISSING>"
            phone = js.get("telephone") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            tmp = []
            hours = js.get("openingHoursSpecification")
            if hours:
                for h in hours[:7]:
                    day = h.get("dayOfWeek")
                    if str(day).find("/") != -1:
                        day = str(day).split("/")[-1].strip()
                    opens = h.get("opens")
                    closes = h.get("closes")
                    line = f"{day} {opens} - {closes}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
