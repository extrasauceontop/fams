import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from proxyfier import ProxyProviders


def fetch_data(sgw: SgWriter):

    locator_domain = "https://theoldnoconabootfactory.com/"
    api_url = "https://www.powr.io/map/u/01008607_1602195050#platform=shopify&url=https%3A%2F%2Ftheoldnoconabootfactory.com%2Fpages%2Flocations"
    session = SgRequests(proxy_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    print(r.response.text)
    js_block = r.text.split('"locations":')[1].split(',"map_display"')[0].strip()
    js = json.loads(js_block)
    for j in js:

        ad = "".join(j.get("address"))
        page_url = "https://theoldnoconabootfactory.com/pages/locations"
        location_name = j.get("name") or "<MISSING>"
        street_address = ad.split(",")[0].strip()
        street_address_slug = street_address.split()[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    f'//p[./a[contains(text(), "{street_address_slug}")]]/following-sibling::p[1]//text()'
                )
            )
            or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
