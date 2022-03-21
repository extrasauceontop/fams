import ssl
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.firefox.options import Options

options = Options()
options.set_preference("geo.prompt.testing", True)
options.set_preference("geo.prompt.testing.allow", True)
options.set_preference(
    "geo.provider.network.url",
    'data:application/json,{"location": {"lat": 51.47, "lng": 0.0}, "accuracy": 100.0}',
)
options.add_argument("--headless")

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    start_url = "https://themobilegeneration.com/locations/"
    domain = "themobilegeneration.com"

    with SgFirefox(firefox_options=options) as driver:
        driver.get(start_url)
        sleep(5)
        driver.execute_script("window.scrollBy(0, 250)")
        dom = etree.HTML(driver.page_source)
        all_locations = dom.xpath('//tr[contains(@class, "wpgmaps_mlist_row")]')
        all_states = driver.find_elements_by_xpath("//select[@data-map-id]/option")[1:]
        for i in range(0, len(all_states)):
            all_states = driver.find_elements_by_xpath("//select[@data-map-id]/option")[
                1:
            ]
            driver.execute_script("scroll(0, 0);")
            sleep(5)
            try:
                driver.find_element_by_xpath(
                    '//select[contains(@data-wpgmza-filter-widget-class, "Dropdown")]'
                ).click()
            except Exception:
                pass
            all_states[i].click()
            sleep(5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(3)
            dom = etree.HTML(driver.page_source)
            all_locations += dom.xpath('//tr[contains(@class, "wpgmaps_mlist_row")]')
            driver.find_element_by_xpath('//a[contains(text(), "Next")]').click()
            sleep(5)
            dom = etree.HTML(driver.page_source)
            all_locations += dom.xpath('//tr[contains(@class, "wpgmaps_mlist_row")]')

        for poi_html in all_locations:
            raw_data = poi_html.xpath(".//td/text()")
            raw_address = raw_data[1].split(",")
            phone = poi_html.xpath('./td/p[strong[contains(text(), "Phone")]]/text()')
            phone = phone[0] if phone else ""
            hoo = poi_html.xpath('./td/p[strong[contains(text(), "Hours:")]]/text()')
            hoo = " ".join(hoo)
            zip_code = ""
            if len(raw_address[2].split()) == 2:
                zip_code = raw_address[2].split()[1]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=raw_data[0],
                street_address=raw_address[0],
                city=raw_address[1],
                state=raw_address[2].split()[0],
                zip_postal=zip_code,
                country_code=raw_address[-1],
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
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
