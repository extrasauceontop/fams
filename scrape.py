from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs


def get_data():
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    session = SgRequests()
    start_url = "https://www.dreamdoors.co.uk/kitchen-showrooms"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
    )
    x = 0
    for code in all_codes:

        formdata = {
            "option": "com_ajax",
            "module": "dreamdoors_store_finder",
            "postcode": code,
            "format": "raw",
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        response = session.post(start_url, data=formdata, headers=headers).json()

        try:
            if "error" in response.keys():
                continue
        except Exception:
            pass

        locator_domain = "dreamdoors.co.uk"
        page_url = response[0]["url"]
        location_name = response[0]["name"]

        page_response = session.get(page_url).text
        lines = page_response.split("\n")
        for line in lines:
            if "dd_location.map_initialize" in line:
                geo = line.split(", ")
                latitude = geo[-2]
                longitude = geo[-1].replace(");", "")

        soup = bs(page_response, "html.parser")
        address_parts = [
            part.strip()
            for part in soup.find("div", attrs={"class": "address"})
            .text.strip()
            .split("\n")
        ][1:]

        address = address_parts[0]
        zipp = address_parts[-1]

        if len(address_parts) == 3:
            city = address_parts[-2]
            state = "<MISSING>"

        if len(address_parts) == 4:
            city = address_parts[-3]
            state = address_parts[-2]

        if len(address_parts) > 4:
            address = address + " " + address_parts[1]
            city = address_parts[-3]
            state = address_parts[-2]

        x = x + 1

        store_number = response[0]["id"]

        phone = (
            soup.find("div", attrs={"class": "telephone"})
            .find("a")["href"]
            .replace("tel:", "")
        )
        location_type = "<MISSING>"
        times = soup.find_all("span", attrs={"class": "time"})

        y = 0
        hours = ""
        for time_part in times:
            day = days[y]
            y = y + 1
            time = time_part.text.strip()
            hours = hours + day + " " + time + ", "
        country_code = "UK"
        hours = hours[:-2]
        if "coming soon" in address.lower():
            continue

        if city == "Springkerse Industrial Estate":
            address = address + " " + city
            city = state
            state = "<MISSING>"
        yield {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": address,
            "state": state,
            "zip": zipp,
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
            "country_code": country_code,
        }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"], is_required=False),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
