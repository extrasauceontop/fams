from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA]
)

for search_lat, search_lon in search:
    print(search_lat, search_lon)