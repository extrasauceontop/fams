from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import ssl
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest
import json

ssl._create_default_https_context = ssl._create_unverified_context
crawl_state = CrawlStateSingleton.get_instance()


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
                    if "longitude" in json.loads(html_string[start : end + 1]).keys():
                        break

                except Exception:
                    pass
        count = count + 1

    return json_objects


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


def reset_sessions(data_url):
    s = SgRequests()

    driver = get_driver(data_url, "active")

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                driver.quit()
                return [s, headers, response_text]

        except Exception:
            driver.quit()
            continue


def get_data():
    log = sglog.SgLogSetup().get_logger(logger_name="carehomes")
    if not crawl_state.get_misc_value("got_urls"):
        breaker = 0
        while True:
            try:
                data_url = "https://www.carehome.co.uk/"
                new_sess = reset_sessions(data_url)

                s = new_sess[0]
                headers = new_sess[1]
                response_text = new_sess[2]
                break
            except Exception:
                breaker = breaker + 1
                if breaker == 10:
                    raise Exception

        soup = bs(response_text, "html.parser")

        strong_tags = soup.find(
            "div", attrs={"class": "seo_links seo_links_country"}
        ).find_all("strong")
        country_urls = []
        location_urls = []
        for strong_tag in strong_tags:
            a_tag = strong_tag.find("a")
            url = a_tag["href"]

            if "searchcountry" in url:
                country_urls.append("https://www.carehome.co.uk" + url)

        for country_url in country_urls:

            response = s.get(country_url, headers=headers)
            response_text = response.text
            if len(response_text.split("div")) > 2:
                pass
            else:
                breaker = 0
                while True:
                    try:
                        new_sess = reset_sessions(country_url)

                        s = new_sess[0]
                        headers = new_sess[1]
                        response_text = new_sess[2]
                        break

                    except Exception:
                        breaker = breaker + 1
                        if breaker == 10:
                            raise Exception
                        continue

            soup = bs(response_text, "html.parser")
            search_length = int(
                soup.find_all("a", attrs={"class": "page-link"})[-2].text.strip()
            )

            count = 1
            while count < search_length + 1:
                if count == 1:
                    search_url = country_url
                else:
                    search_url = country_url + "/startpage/" + str(count)
                response = s.get(search_url, headers=headers)
                response_text = response.text
                log.info(search_url)
                if len(response_text.split("div")) > 2:
                    pass
                else:
                    y = 0
                    while True:
                        y = y + 1
                        if y == 10:
                            raise Exception
                        log.info("page_url_fail: " + str(y))
                        try:
                            new_sess = reset_sessions(search_url)

                            s = new_sess[0]
                            headers = new_sess[1]
                            response_text = new_sess[2]
                            break
                        except Exception:
                            continue

                # raise Exception
                soup = bs(response_text, "html.parser")

                div_tags = soup.find_all("div", attrs={"class": "search-result"})
                for div_tag in div_tags:
                    try:
                        location_url = div_tag.find(
                            "a", attrs={"class": "search-result-name"}
                        )["href"]
                    except Exception:
                        a_tags = div_tag.find_all("a")
                        for a_tag in a_tags:
                            try:
                                location_url = a_tag["href"]
                            except Exception:
                                pass

                    if location_url in location_urls or "#reviews" in location_url:
                        pass
                    else:
                        crawl_state.push_request(SerializableRequest(url=location_url))
                count = count + 1
        crawl_state.set_misc_value("got_urls", True)

    num_urls = len(crawl_state.request_stack_iter())
    x = 0
    for request_url in crawl_state.request_stack_iter():
        location_url = request_url.url
        x = x + 1

        if "searchazref" not in location_url:
            continue

        try:
            response = s.get(location_url, headers=headers)

        except Exception:
            x = 0
            while True:
                x = x + 1
                try:
                    new_sess = reset_sessions(location_url)

                    s = new_sess[0]
                    headers = new_sess[1]
                    response_text = new_sess[2]
                    break

                except Exception:
                    if x == 10:
                        raise Exception

        response_text = response.text
        log.info("URL " + str(x) + "/" + str(num_urls))
        log.info(location_url)

        if "404 - Page Missing" in response_text:
            continue

        if len(response_text.split("div")) > 2:
            pass
        else:
            y = 0
            while True:
                y = y + 1
                log.info("location_url_fail: " + str(y))
                try:
                    new_sess = reset_sessions(location_url)

                    s = new_sess[0]
                    headers = new_sess[1]
                    response_text = new_sess[2]
                    break
                except Exception:
                    continue

        soup = bs(response_text, "html.parser")

        locator_domain = "carehome.co.uk"
        page_url = location_url
        location_name = (
            soup.find("div", attrs={"class": "profile-header-left"})
            .find("h1")
            .text.strip()
        )

        try:
            check = (
                soup.find("div", attrs={"class": "profile-header-left"})
                .find("small")
                .text.strip()
            )
            check = check
            continue

        except Exception:
            pass

        address_parts = soup.find("meta", attrs={"property": "og:title"})[
            "content"
        ].split(",")

        try:
            address = address_parts[1].strip()
            city = address_parts[-2].strip()
            state_zipp_parts = address_parts[-1].split(" |")[0].split(" ")
            state_parts = state_zipp_parts[:-2]
            state = ""
            for part in state_parts:
                state = state + part + " "
            state = state.strip().replace("County ", "")

            zipp = state_zipp_parts[-2] + " " + state_zipp_parts[-1]
        except Exception:
            if len(address_parts) == 1:
                address = "<MISSING>"
                city = "<MISSING>"
                state = "".join(part for part in address_parts[0].split(" ")[:-2])
                zipp = (
                    address_parts[0].split(" ")[1]
                    + " "
                    + address_parts[0].split(" ")[2]
                )

            else:
                raise Exception

        country_code = "UK"
        store_number = location_url.split("/")[-1]

        try:
            phone = ""
            phone_link = soup.find("button", attrs={"id": "brochure_phone"})["href"]
            phone_response = s.get(phone_link, headers=headers).text
            if len(phone_response.split("div")) > 2:
                pass
            else:
                y = 0
                while True:
                    y = y + 1
                    log.info("phone_url_fail: " + str(y))
                    try:
                        new_sess = reset_sessions(phone_link)

                        s = new_sess[0]
                        headers = new_sess[1]
                        phone_response = new_sess[2]
                        break
                    except Exception:
                        if y == 5:
                            phone == "<INACCESSIBLE>"
                            raise Exception
                        continue
            response_soup = bs(phone_response, "html.parser")
            phone = (
                response_soup.find("div", attrs={"class": "contacts_telephone"})
                .find("a")
                .text.strip()
            )
        except Exception:
            if phone == "<INACCESSIBLE>":
                pass
            else:
                phone = "<MISSING>"

        geo_json = extract_json(response_text.split('geo":')[1].split("reviews")[0])[0]
        latitude = geo_json["latitude"]
        longitude = geo_json["longitude"]
        hours = "<MISSING>"

        try:
            location_type = [
                item.strip()
                for item in soup.find("div", attrs={"class": "row profile-row"})
                .text.strip()
                .split("Care Provided")[1]
                .split("Type of Service")[1]
                .split("\n")
                if len(item) > 2
            ][0] + [
                item.strip()
                for item in soup.find("div", attrs={"class": "row profile-row"})
                .text.strip()
                .split("Care Provided")[1]
                .split("Type of Service")[1]
                .split("\n")
                if len(item) > 2
            ][
                1
            ]

        except Exception:
            location_type = "<MISSING>"

        phone = phone.split("ext")[0].strip()
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
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
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
