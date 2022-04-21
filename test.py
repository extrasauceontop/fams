from sgrequests import SgRequests
import requests

url = "https://www.bobbibrowncosmetics.com/rpc/jsonrpc.tmpl"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Accept": "*/*",
}
params = (("dbgmethod", "locator.doorsandevents"),)
data = {
    "JSONRPC": '[{"method":"locator.doorsandevents","id":2,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, STORE_TYPE, LONGITUDE, LATITUDE","radius":"","country":"United States","region_id":"0,47,27","latitude":33.0218117,"longitude":-97.12516989999999,"uom":"mile","_TOKEN":"b6a2036fda64fc609a1f77f72fcef03bdccde0f9,df93f53a98d3eac0d569475de97dc8d9e8fd3543,1650031353"}]}]',
}

session = SgRequests()
response = requests.post(url, headers=headers, params=params, data=data)
print(response.status_code)

with open("file.txt", "w", encoding="utf-8") as output:
    print(response.text, file=output)