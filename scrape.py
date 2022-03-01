import base64
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest


def get_cookies(session):
    out = dict()
    r = session.get("https://www.ingles-pharmacy.com/inweb/")
    for k, v in r.cookies.items():
        out[k] = v

    return out


def get_csrf(session, headers, cookies):
    data = {"formParams": '""'}
    url = "https://www.ingles-pharmacy.com/inweb/appload.htm"
    r = session.post(url, headers=headers, cookies=cookies, data=data)
    token = r.json()["token"][0]

    return token


def get_ids(session, headers, cookies):
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
    api = "https://www.ingles-pharmacy.com/inweb/getStoreList.htm"
    for lat, lng in search:
        data = {
            "formParams": '{"storeData":"","lat":'
            + f'"{lat}","lng":'
            + f'"{lng}","loggedIn":0'
            + "}"
        }

        r = session.post(api, data=data, headers=headers, cookies=cookies)
        r.json()

        if r.json().get("status") == "FAILURE":
            continue
        js = r.json()["data"]["stores"]["stores_list"]

        for j in js:
            latitude = j["latitude"]
            longitude = j["longitude"]
            search.found_location_at(latitude, longitude)
            crawl_state.push_request(SerializableRequest(url=j["id"]))

    crawl_state.set_misc_value("got_urls", True)


def get_data(_id, sgw: SgWriter, session, headers, cookies):
    locator_domain = "https://www.ingles-pharmacy.com/"
    _id = _id.replace("/", "")
    data = {"formParams": '{"store_id":"' + _id + '","isLogged":"0"}'}
    api = "https://www.ingles-pharmacy.com/inweb/getStoreDetails.htm"
    r = session.post(api, headers=headers, data=data, cookies=cookies)
    j = r.json()["data"]["stores"]

    location_name = j.get("store_name")
    slug = base64.b64encode(_id.encode("utf8")).decode("utf8")
    page_url = f"https://www.ingles-pharmacy.com/inweb/#/store/details/{slug}"
    street_address = j.get("addressline1")
    city = j.get("city")
    state = j.get("state")
    postal = j.get("zip")
    phone = j.get("phone")
    latitude = j.get("latitude")
    longitude = j.get("longitude")
    store_number = j.get("store_identifier")

    _tmp = []
    hours = j.get("hours") or []
    for h in hours:
        day = h.get("day")
        inter = h.get("hours")
        _tmp.append(f"{day}: {inter}")
    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter, session, headers, cookies):
    if not crawl_state.get_misc_value("got_urls"):
        get_ids(session, headers, cookies)

    ids = [loc.url for loc in crawl_state.request_stack_iter()]

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, _id, sgw, session, headers, cookies): _id
            for _id in ids
        }
        for future in futures.as_completed(future_to_url):
            future.result()


def scrape():
    session = SgRequests()
    cookies = get_cookies(session)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "csrfPreventionSalt": "",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.ingles-pharmacy.com",
        "Connection": "keep-alive",
        "Referer": "https://www.ingles-pharmacy.com/inweb/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    csrf = get_csrf(session, cookies, headers)
    headers["csrfPreventionSalt"] = csrf

    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer, session, headers, cookies)


crawl_state = CrawlStateSingleton.get_instance()
x = 0
while True:
    x = x + 1
    if x == 100:
        raise Exception
    try:
        scrape()
        break

    except Exception:
        continue
