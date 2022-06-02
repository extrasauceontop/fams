from sgselenium import SgChrome
from proxyfier import ProxyProviders


if __name__ == "__main__":
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    url = "https://www.luckysupermarkets.com/stores/?coordinates=39.64096403685537,-112.39632159999998&zoom=5"
    with SgChrome(user_agent=user_agent, is_headless=True, block_third_parties=False) as driver:
        driver.get(url)
        response = driver.page_source

    print(response)