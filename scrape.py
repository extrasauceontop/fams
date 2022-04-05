from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
from sgpostal.sgpostal import parse_address_intl
from html import unescape
from bs4 import BeautifulSoup as bs


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
                    if "pagesMap" in html_string[start : end + 1]:
                        json_objects.append(json.loads(html_string[start : end + 1]))
                    else:
                        pass
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():
    start_of_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.responsiveAbsoluteChildrenPosition%3Atrue%2Cspecs.thunderbolt.byRefV2%3Atrue%2Cspecs.thunderbolt.DatePickerPortal%3Atrue%2Cspecs.thunderbolt.LinkBarPlaceholderImages%3Atrue%2Cspecs.thunderbolt.carmi_simple_mode%3Atrue%2Cspecs.thunderbolt.final_image_auto_encode%3Atrue%2Cspecs.thunderbolt.prefetchComponentsShapesInBecky%3Atrue%2Cspecs.thunderbolt.inflatePresetsWithNoDefaultItems%3Atrue%2Cspecs.thunderbolt.maskImageCSS%3Atrue%2Cspecs.thunderbolt.SearchBoxModalSuggestions%3Atrue&contentType=application%2Fjson&deviceType=Other&dfCk=6&dfVersion=1.1581.0&excludedSafariOrIOS=false&experiments=bv_removeMenuDataFromPageJson%2Cbv_remove_add_chat_viewer_fixer%2Cdm_enableDefaultA11ySettings%2Cdm_fixStylableButtonProperties%2Cdm_fixVectorImageProperties%2Cdm_linkRelDefaults%2Cdm_migrateToTextTheme&externalBaseUrl=https%3A%2F%2Fwww.dunkindonuts.co.nz&fileId=0740a8de.bundle.min&hasTPAWorkerOnSite=false&isHttps=true&isInSeo=false&isMultilingualEnabled=false&isPremiumDomain=true&isUrlMigrated=true&isWixCodeOnPage=false&isWixCodeOnSite=true&language=en&languageResolutionMethod=QueryParam&metaSiteId=af1383a7-5553-4e3b-8a74-b212a6373a87&module=thunderbolt-features&originalLanguage=en&pageId="
    end_of_url = ".json&quickActionsMenuEnabled=true&registryLibrariesTopology=%5B%7B%22artifactId%22%3A%22editor-elements%22%2C%22namespace%22%3A%22wixui%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.7951.0%22%7D%2C%7B%22artifactId%22%3A%22editor-elements%22%2C%22namespace%22%3A%22dsgnsys%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.7951.0%22%7D%5D&remoteWidgetStructureBuilderVersion=1.229.0&siteId=8660dfe0-866b-4cbb-9177-b5189db59276&siteRevision=491&staticHTMLComponentUrl=https%3A%2F%2Fwww-dunkindonuts-co-nz.filesusr.com%2F&useSandboxInHTMLComp=false&viewMode=desktop"

    session = SgRequests()
    url = "https://www.dunkindonuts.co.nz/locations"
    response = session.get(url).text

    json_objects = extract_json(response)
    loc_dict = json_objects[0]["siteFeaturesConfigs"]["router"]["pagesMap"]

    for location_id in loc_dict.keys():
        json_page_name = loc_dict[location_id]["pageJsonFileName"]
        page_url = start_of_url + json_page_name + end_of_url
        store_number = loc_dict[location_id]["pageId"]

        response = session.get(page_url).json()
        for key in response["props"]["render"]["compProps"].keys():
            needed_id = key
            break

        try:
            if "CLOSED" not in str(response["props"]["render"]["compProps"]):
                response["props"]["render"]["compProps"][needed_id]["mapData"][
                    "locations"
                ][0]["title"]
            else:
                continue
        except Exception:
            continue
        with open("file.txt", "w", encoding="utf-8") as output:
            json.dump(response, output, indent=4)
        locator_domain = "dunkindonuts.co.nz"
        location_name = response["props"]["render"]["compProps"][needed_id]["mapData"][
            "locations"
        ][0]["title"]
        latitude = response["props"]["render"]["compProps"][needed_id]["mapData"][
            "locations"
        ][0]["latitude"]
        longitude = response["props"]["render"]["compProps"][needed_id]["mapData"][
            "locations"
        ][0]["longitude"]

        full_address = response["props"]["render"]["compProps"][needed_id]["mapData"][
            "locations"
        ][0]["address"]
        addr = parse_address_intl(full_address)

        city = addr.city
        if city is None:
            city = "<MISSING>"

        address_1 = addr.street_address_1
        address_2 = addr.street_address_2

        if address_1 is None and address_2 is None:
            address = "<MISSING>"
        else:
            address = (
                (str(address_1) + " " + str(address_2)).strip().replace(" None", "")
            )

        state = addr.state
        if state is None:
            state = "<MISSING>"

        zipp = addr.postcode
        if zipp is None:
            zipp = "<MISSING>"

        country_code = addr.country
        if country_code is None:
            country_code = "<MISSING>"

        location_type = "<MISSING>"

        for key in response["props"]["render"]["compProps"].keys():
            part_check = response["props"]["render"]["compProps"][key]
            for sub_key in part_check.keys():
                if sub_key == "html":
                    phone_check = part_check[sub_key]
                    if (
                        city.lower() in phone_check.lower()
                        or '<p class="font_8" style="line-height:1.7em; font-size:17px;"><span style="font-family:arial'
                        in phone_check.lower()
                    ):
                        phone = unescape(
                            phone_check.replace("\n", "")
                            .replace("</span></span>", "</span>")
                            .split("</span>")[-2]
                            .split(">")[-1]
                            .strip()
                        ).replace("Phone ", "")

        hours_soup = bs(phone_check, "html.parser")
        hours_text = hours_soup.text.strip()

        hours = (
            hours_text.replace("\n", ", ").split(", Mall")[0].replace(" , ", ", ")
        ).strip()

        if hours[-3] == ",":
            hours = hours[:-3]

        if "opening hours" in hours.lower():
            hours = "Temporarily Closed"

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
