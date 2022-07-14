from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import unidecode
from sgpostal.sgpostal import parse_address_intl

def get_data():
    url ="https://www.razer.com/razerstores"
    with SgRequests() as session:
        response = session.get(url).text.replace("<br>", "\n")

        soup = bs(response, "html.parser")
        grids = soup.find_all("div", attrs={"class": "store"})

        for grid in grids:
            locator_domain = "razer.com"
            page_url = "https://www.razer.com" + grid.find("a", attrs={"class": "gtm_learn_more"})["href"][1:]
            location_name = grid.find("div", attrs={"class": "address"}).find("strong").text.strip().replace("\n", " ")

            address_parts = grid.find("div", attrs={"class": "address"}).find("p")
            first_line = address_parts.find("span").text.strip()
            full_address = address_parts.text.strip()
            raw_address = unidecode.unidecode(full_address.replace(first_line, first_line + " ")).replace("\n", " ").replace("\t", "").replace("\r", "")
            while "  " in raw_address:
                raw_address = raw_address.replace("  ", " ")

            addr = parse_address_intl(full_address)
            city = addr.city
            if city is None:
                city = "<MISSING>"

            address_1 = addr.street_address_1
            address_2 = addr.street_address_2

            if address_1 is None and address_2 is None:
                address = "<MISSING>"
            else:
                address = (str(address_1) + " " + str(address_2)).strip()

            state = addr.state
            if state is None:
                state = "<MISSING>"

            zipp = addr.postcode
            if zipp is None:
                zipp = "<MISSING>"

            country_code = addr.country
            if country_code is None:
                country_code = "<MISSING>"

            print(page_url)
            page_response = session.get(page_url).text.replace("<br>", "\n")
            page_soup = bs(page_response, "html.parser")

            try:
                latitude = page_response.split("2!3d")[1].split("!")[0]
                longitude = page_response.split("2!3d")[1].split("!4d")[1].split('"')[0]
            except Exception:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            phone_parts = page_soup.find_all("p", attrs={"class": "p-container lt1"})
            for part in phone_parts:
                if "+" in part.text.strip():
                    phone = part.text.strip().split("+")[1].split("\n")[0]
                    
                    hours = ""
                    for line in part.text.strip().split("\n"):
                        if "AM" in line and "PM" in line:
                            hours = hours + line + ", "
                        
                    break
            print(phone)

            address = address.replace(" None", "")
            location_type = "<MISSING>"
            store_number = "<MISSING>"
            hours = hours[:-2]

            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "store_number": store_number,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
                "country_code": country_code,
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
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


if __name__ == "__main__":
    scrape()
