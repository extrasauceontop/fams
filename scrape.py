import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = re.findall(r"\d{5}", line)
    if post:
        adr = parse_address(International_Parser(), line, postcode=post.pop())
    else:
        adr = parse_address(International_Parser(), line)

    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    postal = adr.postcode or SgRecord.MISSING

    return street, postal


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_tree(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(url, headers=headers)
    return html.fromstring(r.text)


def get_additional(page_url):
    tree = get_tree(page_url)
    phone = "".join(tree.xpath("//div[@class='store-phone store-txt']/text()"))
    phone = (
        phone.replace("Phone", "")
        .replace("Tel", "")
        .replace("ef", "")
        .replace("f", "")
        .replace(".", "")
        .replace(":", "")
        .strip()
    )
    text = "".join(tree.xpath("//iframe/@src"))
    lat, lng = get_coords_from_embed(text)
    hoo = (
        ";".join(tree.xpath("//div[@class='store-time store-txt']//text()"))
        .replace("â", "-")
        .strip()
    )

    return phone, lat, lng, hoo


def fetch_data(sgw: SgWriter):
    tree = get_tree("https://www.munichsports.com/en/munich-stores")
    divs = tree.xpath("//div[@class='shop-info']")
    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='store']/text()")).strip()
        city = "".join(d.xpath(".//span[@class='city']/text()")).strip()
        slug = "".join(d.xpath(".//div[@class='shop-name']/a/@href"))
        page_url = f"https://www.munichsports.com{slug}"
        line = d.xpath(
            ".//div[@class='shop-address']/text()|.//div[@class='shop-address']/div/text()"
        )
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = " ".join(line).upper().replace(location_name, "").strip()
        if "OUTLETS" in raw_address:
            raw_address = raw_address.split("OUTLETS")[1].strip()
        if "OUTLET" in raw_address:
            raw_address = raw_address.split("OUTLET")[1].strip()
        if raw_address.startswith("C.C.") or raw_address.startswith("CC"):
            raw_address = ",".join(raw_address.split(",")[1:]).strip()
        if raw_address.startswith("-") or raw_address.startswith(","):
            raw_address = raw_address[1:].strip()

        street_address, postal = get_international(raw_address)
        phone, latitude, longitude, hours_of_operation = get_additional(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="ES",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.munichsports.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
