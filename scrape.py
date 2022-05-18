from sgselenium import SgChrome

with SgChrome() as driver:
    driver.get("https://www.zorbaz.com/")
    driver.save_screenshot("zorbas.png")
    response = driver.page_source
    with open("index.html", "w", encoding="utf-8") as output:
        print(response, file=output)
