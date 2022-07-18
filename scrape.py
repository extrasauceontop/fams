# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from proxyfier import ProxyProviders
# from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(proxy_country="be", proxy_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER)

    start_url = "https://www.gabriels.be/en/views/ajax?_wrapper_format=drupal_ajax"
    domain = "gabriels.be"
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    frm = {
        "view_name": "gas_stations",
        "view_display_id": "map_list",
        "view_args": "",
        "view_path": "/node/78",
        "view_base_path": "",
        "view_dom_id": "c270031950bd579720621f90a9d7455e2c14d868f70ac2d0b2f3e827b52c48b6",
        "pager_element": "0",
        "field_geolocation_proximity": "30",
        "field_brand_target_id": "1",
        "node_brand_filter": "0",
        "actions[submit]": "Apply",
        "actions[reset]": "Reset",
        "page": "1",
        "_drupal_ajax": "1",
        "ajax_page_state[theme]": "dms_theme",
        "ajax_page_state[theme_token]": "",
        "ajax_page_state[libraries]": "ajax_loader/ajax_loader.throbber,better_exposed_filters/auto_submit,better_exposed_filters/general,chosen/drupal.chosen,chosen_lib/chosen.css,dms_theme/fonts,dms_theme/gas_stations__map,dms_theme/global_scripts,dms_theme/global_styles,dms_theme/icon_fonts,eu_cookie_compliance/eu_cookie_compliance_bare,geolocation/location_input.geocoder,geolocation/map_center.fitlocations,geolocation/map_center.static_location,geolocation_google_maps/commonmap.google,geolocation_google_maps/google,geolocation_google_maps/mapfeature.control_locate,geolocation_google_maps/mapfeature.control_maptype,geolocation_google_maps/mapfeature.control_zoom,geolocation_google_maps/mapfeature.marker_clusterer,geolocation_google_maps/mapfeature.marker_infowindow,geolocation_google_places_api/geolocation_google_places_api.geocoder.googleplacesapi,paragraphs/drupal.paragraphs.unpublished,system/base,views/views.ajax,views/views.module,views_infinite_scroll/views-infinite-scroll",
    }
    data = session.post(start_url, headers=hdr, data=frm).json()
    with open("file.txt", "w", encoding="utf-8") as output:
        print(data, file=output)
    dom = etree.HTML(data[1]["data"])

    all_locations = dom.xpath('//div[@class="location-content"]')
    x = 0
    for poi_html in all_locations:
        x = x+1
        # if x == 10:
        #     return
        location_name = poi_html.xpath('.//span[@class="field-content"]/text()')[0]
        raw_address = poi_html.xpath('.//div[@class="field-content"]/text()')[0]
        # addr = parse_address_intl(raw_address)
        # street_address = addr.street_address_1
        # if addr.street_address_2:
        #     street_address += " " + addr.street_address_2
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        url = poi_html.xpath(".//a/@href")[-1]
        page_url = urljoin("https://www.gabriels.be/en/find-a-gasstation", url)

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        latitude = loc_dom.xpath('//meta[@property="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@property="longitude"]/@content')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address="<LATER>",
            # city=addr.city,
            # state=addr.state,
            # zip_postal=addr.postcode,
            city="<LATER>",
            state="<LATER>",
            zip_postal="<LATER>",
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
            raw_address=raw_address,
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
