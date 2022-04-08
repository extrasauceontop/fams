from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("homedepot_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    states = []
    url = "https://www.homedepot.com/l/storeDirectory"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="store-directory__state-link' in line:
            items = line.split('<a class="store-directory__state-link')
            for item in items:
                if 'href="https://www.homedepot.com/l/' in item:
                    lurl = item.split('href="')[1].split('"')[0]
                    if lurl not in states:
                        states.append(lurl)
    for state in states:
        Found = True
        while Found:
            logger.info(state)
            r2 = session.get(state, headers=headers)
            for line2 in r2.iter_lines():
                if '","url":"https://www.homedepot.com/' in line2:
                    items = line2.split('","url":"https://www.homedepot.com/')
                    for item in items:
                        if '","phone":' in item:
                            Found = False
                            surl = "https://www.homedepot.com/" + item.split('"')[0]
                            if surl not in locs:
                                locs.append(surl)

    logger.info(len(locs))

    for loc in locs:
        if "/designcenter" in loc:
            continue
        if loc == "https://www.homedepot.com/l/storeDirectory":
            continue

        Found = True
        rcount = 0
        while Found and rcount <= 3:
            try:
                rcount = rcount + 1
                logger.info("Pulling Location %s..." % loc)
                website = "homedepot.com"
                typ = "<MISSING>"
                hours = ""
                name = ""
                add = ""
                city = ""
                state = ""
                zc = ""
                country = "US"
                store = ""
                phone = ""
                lat = ""
                lng = ""
                phone = ""
                r2 = session.get(loc, headers=headers)
                for line2 in r2.iter_lines():
                    if "<h1" in line2:
                        name = line2.split("<h1")[1].split('">')[1].split("<")[0]
                    if '"stores":[{' in line2:
                        Found = False
                        add = line2.split('"street":"')[1].split('"')[0]
                        city = line2.split('"city":"')[1].split('"')[0]
                        state = line2.split('"state":"')[1].split('"')[0]
                        zc = line2.split('"postalCode":"')[1].split('"')[0]
                        store = line2.split('"storeId":"')[1].split('"')[0]
                        lng = line2.split('"lng":')[1].split("}")[0]
                        lat = line2.split('"lat":')[1].split(",")[0]
                    if '"openingHours":["' in line2:
                        hours = (
                            line2.split('"openingHours":["')[1]
                            .split('"],')[0]
                            .replace('","', "; ")
                            .replace('"', "")
                        )
                    if phone == "" and 'href="tel:' in line2:
                        phone = line2.split('href="tel:')[1].split('"')[0]
                if hours == "":
                    hours = "<MISSING>"
                if state == "PR":
                    country = "Puerto Rico"
                    state = "<MISSING>"
                if state == "VI":
                    country = "US Virgin Islands"
                    state = "<MISSING>"
                if state == "GU":
                    country = "Guam"
                    state = "<MISSING>"
                
                if name == "" or name == "<MISSING>":
                    print(r2.text)
                    raise Exception

                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )

            except Exception:
                if rcount == 3:
                    raise Exception

                else:
                    pass

    website = "homedepot.com"
    typ = "<MISSING>"
    hours = "Mon-Sat 9:00am - 7:00pm; Sun 10:00am - 5:00pm"
    name = "San Diego"
    add = "9480 Carroll Park Drive"
    city = "San Diego"
    state = "CA"
    zc = "92121"
    country = "US"
    store = "<MISSING>"
    phone = "858-812-8680"
    lat = "32.8865868"
    lng = "-117.1739095"
    loc = "https://hddc-appointment.extapps.homedepot.com/storeSelection"
    yield SgRecord(
        locator_domain=website,
        page_url=loc,
        location_name=name,
        street_address=add,
        city=city,
        state=state,
        zip_postal=zc,
        country_code=country,
        phone=phone,
        location_type=typ,
        store_number=store,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours,
    )
    website = "homedepot.com"
    typ = "<MISSING>"
    hours = "Mon-Sat 10:00am - 7:00pm; Sun 10:00am - 6:00pm"
    name = "Rockville"
    add = "12087 Rockville Pike"
    city = "Rockville"
    state = "MD"
    zc = "20852"
    country = "US"
    store = "<MISSING>"
    phone = "301-692-3700"
    lat = "39.0563569"
    lng = "-77.1188593"
    loc = "https://www.homedepot.com/c/designcenter"
    yield SgRecord(
        locator_domain=website,
        page_url=loc,
        location_name=name,
        street_address=add,
        city=city,
        state=state,
        zip_postal=zc,
        country_code=country,
        phone=phone,
        location_type=typ,
        store_number=store,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours,
    )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
