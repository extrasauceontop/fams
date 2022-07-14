from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import unidecode
import json


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
                except Exception as e:
                    print(html_string[start : end + 1])
                    print(e)
                    pass
        count = count + 1

    return json_objects


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

            

            print(page_url)
            page_response = session.get(page_url).text.replace("<br>", "\n")
            
            page_json = extract_json(page_response.split("og:type")[1])

            with open("file.txt", "w", encoding="utf-8") as output:
                json.dump(page_json, output, indent=4)



            

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
