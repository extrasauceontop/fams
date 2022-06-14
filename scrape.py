from sgselenium import SgFirefox

url = "https://www.galerieslafayette.com/"
with SgFirefox(is_headless=True, block_third_parties=False) as driver:
    driver.get(url)
    response = driver.page_source
    
with open("file.txt", "w", encoding="utf-8") as output:
    print(response)