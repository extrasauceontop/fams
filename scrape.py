from sgselenium import MagiConfig

url = "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/default/Stores-GetNearestStores?latitude=33.4306545&longitude=-86.7919009&countryCode=US&distanceUnit=mi&maxdistance=25&social=false"
MagiConfig.find_sgselenium(url, find_first=True)