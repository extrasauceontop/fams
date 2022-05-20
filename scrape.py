from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

initial_url = "https://www.sytner.co.uk/dealer-locator/?postcode=london&distance=0&franchiseHash="

with SgChrome() as driver:
    driver.get(initial_url)

    html = driver.page_source

soup = bs(html, "html.parser")


grids = soup.find_all("div", attrs={"class": "row-fluid row-t2crq"})
for grid in grids:
    locator_domain = "sytner.co.uk"
    page_url = grid.find("a", attrs={"title": "Full Details"})["href"]
    location_name = grid.find("h3").text.strip()
    address = grid.find("span", attrs={"class": "address-line1"}).text.strip()[:-1]
    city = grid.find("span", attrs={"class": "address-city"}).text.strip()[:-1]
    state = grid.find("span", attrs={"class": "address-county"}).text.strip()[:-1]
    zipp = grid.find("span", attrs={"class": "address-postcode"}).text.strip()
    country_code = "UK"
    phone = grid.find("div", attrs={"class": "location-no"}).find("a")["href"]
    phone = phone.split(":")[1]

    location_type = grid.find("span").text.strip()
    latitude = grid.find("a", attrs={"title": "View Location"})["data-latitude"]
    longitude = grid.find("a", attrs={"title": "View Location"})["data-longitude"]
    store_number = grid.find("a", attrs={"title": "View Location"})["data-id"]
    hours = "<INACCESSIBLE>"

    locator_domains.append(locator_domain)
    page_urls.append(page_url)
    location_names.append(location_name)
    street_addresses.append(address)
    citys.append(city)
    states.append(state)
    zips.append(zipp)
    country_codes.append(country_code)
    store_numbers.append(store_number)
    phones.append(phone)
    location_types.append(location_type)
    latitudes.append(latitude)
    longitudes.append(longitude)
    hours_of_operations.append(hours)

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)
