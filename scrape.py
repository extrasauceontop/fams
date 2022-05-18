from sgselenium import SgChrome
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context


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
                except Exception:
                    pass
        count = count + 1

    return json_objects


with SgChrome() as driver:
    driver.get("https://www.zorbaz.com/locations")
    driver.save_screenshot("zorbas.png")
    response = driver.page_source

json_objects = extract_json(response.split("APOLLO_STATE")[1])[0]

print(json_objects)
