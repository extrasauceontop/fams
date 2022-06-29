from sgselenium import SgChrome

if __name__ == "__main__":
    base_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants?includePrivate=false"
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
        block_third_parties=False
    ) as driver:
        driver.get(base_url)
        response = driver.page_source

    with open("file.txt", "w", encoding="utf-8") as output:
        print(response, file=output)
