import json
import ssl

from bs4 import BeautifulSoup

from sgselenium.sgselenium import SgChrome

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from proxyfier import ProxyProviders

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://easyhome.ca/store/all"

    with SgChrome(proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER, block_third_parties=True, is_headless=True, proxy_country="ca") as driver:
        driver.get(base_link)
        text = driver.page_source
        with open("file.txt", "w", encoding="utf-8") as output:
            print()
        soup = BeautifulSoup(text, "lxml")

        k = json.loads(soup.text, strict=False)
        for index, i in enumerate(k):
            st = i["address1"]
            lat = i["latitude"]
            log = i["longitude"]
            postal = i["zip"].upper()
            name = i["storeName"]
            storeCode = i["storeCode"]
            state = i["state"].split("-")[0]
            city = i["city"]
            phone = i["phone"]
            if "saturdayClose" in i or "saturdayOpen" in i:
                if i["saturdayOpen"] is not None:

                    index = 2
                    char = ":"
                    saturdayOpen = (
                        i["saturdayOpen"][:index]
                        + char
                        + i["saturdayOpen"][index + 1 :]
                        + ""
                        + str(0)
                    )

                    index1 = 2
                    char = ":"
                    saturdayClose = (
                        i["saturdayClose"][:index1]
                        + char
                        + i["saturdayClose"][index1 + 1 :]
                        + ""
                        + str(0)
                    )

                    index2 = 2
                    char = ":"
                    weekdayOpen = (
                        i["weekdayOpen"][:index2]
                        + char
                        + i["weekdayOpen"][index2 + 1 :]
                        + ""
                        + str(0)
                    )

                    index3 = 2
                    char = ":"
                    weekdayClose = (
                        i["weekdayClose"][:index3]
                        + char
                        + i["weekdayClose"][index3 + 1 :]
                        + ""
                        + str(0)
                    )

                    time = (
                        "Mon-Fri:"
                        + " "
                        + str(weekdayOpen)
                        + " - "
                        + str(weekdayClose)
                        + ", Sat: "
                        + saturdayOpen.replace("90:0", "09:00")
                        + " - "
                        + str(saturdayClose)
                    ).replace(
                        "saturdayOpen None saturdayClose None weekdayOpen None weekdayClose None",
                        "",
                    )

                else:
                    time = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain="https://easyhome.ca",
                    page_url="https://easyhome.ca/locations",
                    location_name=name,
                    street_address=st,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code="CA",
                    store_number=storeCode,
                    phone=phone,
                    location_type="",
                    latitude=lat,
                    longitude=log,
                    hours_of_operation=time,
                )
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
