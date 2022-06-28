from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import re
from proxyfier import ProxyProviders
import unidecode
from sgpostal.sgpostal import parse_address_intl

def check_response(response):
    try:
        if '<div id="mapa' not in response:
            return False

        else:
            return True

    except Exception:
        return False


def get_data():
    url = "https://www.dominospizza.es/tiendas-dominos-pizza"
    with SgRequests(
        response_successful=check_response,
        proxy_country="es",
        proxy_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER
    ) as session:
        response = session.get(url).text

    soup = bs(response, "html.parser")
    grids = soup.find("div", attrs={"id": "listaTiendas"}).find_all("ul")

    for grid in grids:
        zipp_index = -1
        locator_domain = "www.dominospizza.es/"
        page_url = (
            "https://www.dominospizza.es"
            + grid.find("a", attrs={"class": "nm"})["href"]
        )
        location_name = grid.find("span", attrs={"itemprop": "name"}).text.strip()
        latitude = grid.find("li")["data-latitude"]
        longitude = grid.find("li")["data-longitude"]

        full_address = unidecode.unidecode(grid.find("span", attrs={"id": "idLocalidad"}).text.strip())
        addr = parse_address_intl(full_address)

        city = addr.city
        if city is None:
            city = "<MISSING>"

        address_1 = addr.street_address_1
        address_2 = addr.street_address_2

        if address_1 is None and address_2 is None:
            address = "<MISSING>"
        else:
            address = (str(address_1) + " " + str(address_2)).strip().replace(" None", "")

        state = addr.state
        if state is None:
            state = "<MISSING>"

        zipp = addr.postcode
        if zipp is None:
            zipp = "<MISSING>"

        country_code = "ES"
        store_number = (
            grid.find("p", attrs={"id": "tiendaMapaUbicacion"})
            .find("div")["id"]
            .replace("mapa-", "")
        )

        phone = grid.find("span", attrs={"itemprop": "telephone"}).text.strip()
        location_type = "<MISSING>"

        hours = "<MISSING>"
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
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
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


scrape()
