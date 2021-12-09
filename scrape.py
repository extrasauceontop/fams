from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def scrape_malaysia(session, headers):

    response = session.get(
        "https://www.texaschickenmalaysia.com/wp-admin/admin-ajax.php?action=store_search&lat=3.1177&lng=101.67748&max_results=50&search_radius=500&autoload=1",
        headers=headers,
    ).json()

    locs = []
    for location in response:
        locator_domain = "https://www.texaschickenmalaysia.com/"
        page_url = "https://www.texaschickenmalaysia.com/nearest-texas-chicken-store/"
        location_name = location["store"]
        latitude = location["lat"]
        longitude = location["lng"]
        city = location["city"]
        state = location["state"]
        store_number = location["id"]
        address = location["address"]
        zipp = location["zip"]
        phone = "".join(
            character for character in location["phone"] if character.isdigit() is True
        )
        hours = ("daily " + location["bizhour"]).replace("<p>", "").replace("</p>", "")
        if "losed till further notic" in hours.lower():
            continue
        country_code = "Malaysia"
        location_type = "<MISSING>"

        locs.append(
            {
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
        )

    return locs


def scrape_singapore(session, headers):
    response = session.get("https://sg.texaschicken.com/en/Locations").text
    lines = response.split("\n")

    locs = []
    for line in lines:

        if "markers.push" in line:
            line = (
                line.replace("markers.push([", "")
                .replace("]);", "")
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("'", "")
                .split(",")
            )

            locator_domain = "sg.texaschicken.com/"
            page_url = "https://sg.texaschicken.com/en/Locations"
            location_name = line[0]
            latitude = line[2]
            longitude = line[1]
            store_number = line[-1].strip()

            params = {
                "ID": int(store_number),
                "Text": "",
                "isDelivery": "",
                "isWifi": "",
                "isDrive": "",
                "isKidsArea": "",
                "isHandicap": "",
                "isHours": "",
                "_isMall": "",
                "_isBreakfast": "",
                "_isfacility": "",
                "_isfacility2": "",
                "_isfacility3": "",
                "lang": "en",
            }

            location_response = session.post(
                "https://sg.texaschicken.com/Locations/AjaxSearch",
                headers=headers,
                json=params,
            ).text
            location_soup = bs(location_response, "html.parser")

            address_parts = (
                location_soup.find("div", attrs={"class": "col-md-12"})
                .find_all("p")[-1]
                .text.strip()
            )

            address = ""
            address = (
                address_parts.lower()
                .split(" singapore")[0]
                .strip()
                .split("spore")[0]
                .strip()[:-1]
            )

            city = "<MISSING>"
            state = "<MISSING>"
            zipp = address_parts.strip().split(" ")[-1]
            country_code = "Singapore"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours = (
                location_soup.find("p", attrs={"class": "font-15"})
                .text.strip()
                .replace("Opening ", "")
            )

            locs.append(
                {
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
            )

    return locs


def scrape_belarus(session, headers):
    url = "https://texas-chicken.by/en/restorany"

    response = session.get(url, headers=headers).text
    soup = bs(response, "html.parser")

    table_rows = soup.find(
        "div", attrs={"class": "mod_page_map_gr_block info"}
    ).find_all("div", attrs={"class": "row"})[1:]
    locs = []
    lat_lon_parts = response.split("ymaps.Placemark([")[1:]

    x = 0
    for row in table_rows:
        locator_domain = "texas-chicken.by"
        page_url = "https://texas-chicken.by/en/restorany"
        location_name = row.find("div", attrs={"class": "metro"}).text.strip()
        address = row.find("div", attrs={"class": "address"}).text.strip()
        hours = address = (
            "daily: " + row.find("div", attrs={"class": "work"}).text.strip()
        )
        phone = row.find("div", attrs={"class": "phone"}).text.strip()

        location_type = "<MISSING>"
        country_code = "Belarus"
        state = "<MISSING>"
        city = "<MISSING>"
        zipp = "<MISSING>"

        zipp = "<MISSING>"
        store_number = "<MISSING>"

        lat_lon = lat_lon_parts[x]
        latitude = lat_lon.split("],")[0].split(",")[0]
        longitude = lat_lon.split("],")[0].split(",")[1]

        x = x + 1
        locs.append(
            {
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
        )

    return locs


def scrape_bahrain(session, headers):
    response = session.get("https://bahrain.texaschicken.com/en/Locations").text
    lines = response.split("\n")

    locs = []
    for line in lines:

        if "markers.push" in line:
            line = (
                line.replace("markers.push([", "")
                .replace("]);", "")
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("'", "")
                .split(",")
            )

            locator_domain = "bahrain.texaschicken.com/"
            page_url = "https://bahrain.texaschicken.com/en/Locations"
            location_name = line[0]
            latitude = line[2]
            longitude = line[1]
            store_number = line[-1].strip()

            params = {
                "ID": int(store_number),
                "Text": "",
                "isDelivery": "",
                "isWifi": "",
                "isDrive": "",
                "isKidsArea": "",
                "isHandicap": "",
                "isHours": "",
                "_isMall": "",
                "_isBreakfast": "",
                "_isfacility": "",
                "_isfacility2": "",
                "_isfacility3": "",
                "lang": "en",
            }

            location_response = session.post(
                "https://bahrain.texaschicken.com/Locations/AjaxSearch",
                headers=headers,
                json=params,
            ).text
            location_soup = bs(location_response, "html.parser")

            address_parts = (
                location_soup.find("div", attrs={"class": "col-md-12"})
                .find_all("p")[-1]
                .text.strip()
            )

            address = address_parts.lower()

            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "Bahrain"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours = (
                location_soup.find("p", attrs={"class": "font-15"})
                .text.strip()
                .replace("Opening ", "")
                .replace("\r", " ")
                .replace("\n", " ")
            )

            locs.append(
                {
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
            )

    return locs


def scrape_jordan(session, headers):
    response = session.get(
        "http://texaschickenarabia.com/Jordan/en/stores.html", headers=headers
    ).text
    soup = bs(response, "html.parser")

    grids = soup.find_all("div", attrs={"class": "address"})

    locs = []
    for grid in grids:
        locator_domain = "texaschickenarabia.com/Jordan"
        page_url = "http://texaschickenarabia.com/Jordan/en/stores.html"
        location_name = grid.find("p").text.strip()
        address = grid.find("p", attrs={"class": "info"}).text.strip()

        try:
            phone = grid.find_all("p", attrs={"class": "info"})[1].text.strip()
        except Exception:
            phone = "<MISSING>"

        latitude = grid.find("a")["href"].split("@")[1].split(",")[0]
        longitude = grid.find("a")["href"].split("@")[1].split(",")[1]

        city = "<MISSING>"
        store_number = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        location_type = "<MISSING>"
        hours = "<MISSING>"
        country_code = "<MISSING>"

        locs.append(
            {
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
        )

    return locs


def scrape_pakistan(session, headers):
    response = session.get("https://pakistan.texaschicken.com/en/Locations").text
    lines = response.split("\n")

    locs = []
    for line in lines:

        if "markers.push" in line:
            line = (
                line.replace("markers.push([", "")
                .replace("]);", "")
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("'", "")
                .split(",")
            )

            locator_domain = "pakistan.texaschicken.com/"
            page_url = "pakistan.texaschicken.com/en/Locations"
            location_name = line[0]
            latitude = line[2]
            longitude = line[1]
            store_number = line[-1].strip()

            params = {
                "ID": int(store_number),
                "Text": "",
                "isDelivery": "",
                "isWifi": "",
                "isDrive": "",
                "isKidsArea": "",
                "isHandicap": "",
                "isHours": "",
                "_isMall": "",
                "_isBreakfast": "",
                "_isfacility": "",
                "_isfacility2": "",
                "_isfacility3": "",
                "lang": "en",
            }

            location_response = session.post(
                "https://pakistan.texaschicken.com/Locations/AjaxSearch",
                headers=headers,
                json=params,
            ).text
            location_soup = bs(location_response, "html.parser")

            address_parts = (
                location_soup.find("div", attrs={"class": "col-md-12"})
                .find_all("p")[-1]
                .text.strip()
                .replace('"', "")
            )

            address_parts = address_parts.lower().split(", ")

            if address_parts[-1] == "pakistan":
                address = address_parts[0]
                city = address_parts[-3]
                state = address_parts[-2].split(" ")[0]

            else:
                address = address_parts[0]
                city = "<MISSING>"
                state = "<MISSING>"

            zipp = "<MISSING>"
            country_code = "Pakistan"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours = (
                location_soup.find("p", attrs={"class": "font-15"})
                .text.strip()
                .replace("Opening ", "")
                .replace("\r", " ")
                .replace("\n", " ")
            )

            locs.append(
                {
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
            )

    return locs


def scrape_riyadh(session, headers):
    response = session.get("https://riyadh.texaschicken.com/en/Locations").text
    lines = response.split("\n")

    locs = []
    for line in lines:

        if "markers.push" in line:
            line = (
                line.replace("markers.push([", "")
                .replace("]);", "")
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("'", "")
                .split(",")
            )

            locator_domain = "riyadh.pakistan.texaschicken.com/"
            page_url = "https://riyadh.texaschicken.com/en/Locations"
            location_name = line[0]
            latitude = line[2]
            longitude = line[1]
            store_number = line[-1].strip()

            params = {
                "ID": int(store_number),
                "Text": "",
                "isDelivery": "",
                "isWifi": "",
                "isDrive": "",
                "isKidsArea": "",
                "isHandicap": "",
                "isHours": "",
                "_isMall": "",
                "_isBreakfast": "",
                "_isfacility": "",
                "_isfacility2": "",
                "_isfacility3": "",
                "lang": "en",
            }

            location_response = session.post(
                "https://riyadh.texaschicken.com/Locations/AjaxSearch",
                headers=headers,
                json=params,
            ).text
            location_soup = bs(location_response, "html.parser")

            address_parts = (
                location_soup.find("div", attrs={"class": "col-md-12"})
                .find_all("p")[-1]
                .text.strip()
                .replace('"', "")
            )

            address = address_parts.split(", Riyadh")[0]

            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "Riyadh"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours = (
                location_soup.find("p", attrs={"class": "font-15"})
                .text.strip()
                .replace("Opening ", "")
                .replace("\r", " ")
                .replace("\n", " ")
                .replace("\t", " ")
                .replace("                          ", " ")
            )

            locs.append(
                {
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
            )

    return locs


def scrape_uae(session, headers):
    response = session.get("https://uae.texaschicken.com/en/Locations").text
    lines = response.split("\n")

    locs = []
    for line in lines:

        if "markers.push" in line:
            line = (
                line.replace("markers.push([", "")
                .replace("]);", "")
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("'", "")
                .split(",")
            )

            locator_domain = "uae.texaschicken.com"
            page_url = "https://uae.texaschicken.com/en/Locations"
            location_name = line[0]
            latitude = line[2]
            longitude = line[1]
            store_number = line[-1].strip()

            params = {
                "ID": int(store_number),
                "Text": "",
                "isDelivery": "",
                "isWifi": "",
                "isDrive": "",
                "isKidsArea": "",
                "isHandicap": "",
                "isHours": "",
                "_isMall": "",
                "_isBreakfast": "",
                "_isfacility": "",
                "_isfacility2": "",
                "_isfacility3": "",
                "lang": "en",
            }

            location_response = session.post(
                "https://uae.texaschicken.com/Locations/AjaxSearch",
                headers=headers,
                json=params,
            ).text
            location_soup = bs(location_response, "html.parser")

            address_parts = (
                location_soup.find("div", attrs={"class": "col-md-12"})
                .find_all("p")[-1]
                .text.strip()
                .replace('"', "")
                .split(", ")
            )

            address = "".join(part + " " for part in address_parts[:-2])

            if address == "":
                address = "".join(part + " " for part in address_parts)

            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "United Arab Emirates"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours = (
                location_soup.find("p", attrs={"class": "font-15"})
                .text.strip()
                .replace("Opening ", "")
                .replace("\r", " ")
                .replace("\n", " ")
                .replace("\t", " ")
                .replace("                          ", " ")
            )

            if hours.lower() == "daily: closed":
                continue
            locs.append(
                {
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
            )

    return locs


def scrape_newzealand(session, headers):
    url = "https://nz.texaschicken.com/Locations"
    with get_driver(url, "nav-link") as driver:
        response = driver.page_source

    lines = response.split("\n")

    locs = []
    for line in lines:

        if "markers.push" in line:
            line = (
                line.replace("markers.push([", "")
                .replace("]);", "")
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("'", "")
                .split(",")
            )

            locator_domain = "nz.texaschicken.com"
            page_url = url
            location_name = line[0]
            latitude = line[2]
            longitude = line[1]
            store_number = line[-1].strip()

            params = {
                "ID": int(store_number),
                "Text": "",
                "isDelivery": "",
                "isWifi": "",
                "isDrive": "",
                "isKidsArea": "",
                "isHandicap": "",
                "isHours": "",
                "_isMall": "",
                "_isBreakfast": "",
                "_isfacility": "",
                "_isfacility2": "",
                "_isfacility3": "",
                "lang": "en",
            }

            location_response = session.post(
                "https://nz.texaschicken.com/Locations/AjaxSearch",
                headers=headers,
                json=params,
            ).text
            location_soup = bs(location_response, "html.parser")

            address_parts = (
                location_soup.find("div", attrs={"class": "col-md-12"})
                .find_all("p")[-1]
                .text.strip()
                .replace('"', "")
                .split(", ")
            )

            address = "".join(part + " " for part in address_parts[:-2])

            try:
                city = address_parts[-2]
                state = address_parts[-1].split(" ")[0]
                zipp = address_parts[-1].split(" ")[1]

            except Exception:
                city = address_parts[-3]
                state = address_parts[-2]
                zipp = address_parts[-1]

            country_code = "New Zealand"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours = "<MISSING>"
            locs.append(
                {
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
            )

    return locs


def get_data():
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    }

    session = SgRequests()
    url = "https://texaschicken.com/"

    response = session.get(url).text
    soup = bs(response, "html.parser")

    country_list = [
        url.text.strip()
        for url in soup.find_all("option", attrs={"data-tokens": "frosting"})
        if "facebook" not in url["value"]
        and "comingsoon" not in url["value"].lower()
        and url["value"] != "http://www.texaschicken.co.id/"
    ]

    for country in country_list:
        if country == "Malaysia":
            locs = scrape_malaysia(session, headers)

            for loc in locs:
                yield loc

        elif country == "Singapore":
            locs = scrape_singapore(session, headers)

            for loc in locs:
                yield loc

        elif country == "Belarus":
            locs = scrape_belarus(session, headers)

            for loc in locs:
                yield loc

        elif country == "Bahrain":
            locs = scrape_bahrain(session, headers)

            for loc in locs:
                yield loc

        elif country == "Jordan":
            locs = scrape_jordan(session, headers)

            for loc in locs:
                yield loc

        elif country == "Pakistan":
            locs = scrape_pakistan(session, headers)

            for loc in locs:
                yield loc

        elif country == "Riyadh & Eastern KSA":
            locs = scrape_riyadh(session, headers)

            for loc in locs:
                yield loc

        elif country == "United Arab Emirates":
            locs = scrape_uae(session, headers)

            for loc in locs:
                yield loc

        elif country == "New Zealand":
            locs = scrape_newzealand(session, headers)

            for loc in locs:
                yield loc

        else:
            pass


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"],
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
