import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import sglog
import ssl
from proxyfier import ProxyProviders

ssl._create_default_https_context = ssl._create_unverified_context
log = sglog.SgLogSetup().get_logger(logger_name="galerieslafayette.com")


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.galerieslafayette.com/"
    api_url = "https://www.galerieslafayette.com/m/nos-magasins"

    with SgChrome(proxy_country="fr", proxy_provider_escalation_order=ProxyProviders.TEST_PROXY_ESCALATION_ORDER) as driver:
        driver.get(api_url)
        r = driver.page_source
        print(r)
        # log.info(f"{api_url} Response: {r}")

        tree = html.fromstring(r)
        div = (
            "".join(tree.xpath('//script[contains(text(), "stores")]/text()'))
            .split('"stores":')[1]
            .split('},{"name":"Reinsurance"')[0]
            .strip()
        )
        js = json.loads(div)
        log.info(f"Size of first JS: {len(js)}")
        for j in js:
            page_slug = j.get("url")
            page_url = f"https://www.galerieslafayette.com{page_slug}"
            api_slug = "".join(j.get("url")).split("/")[-1].strip()
            if not api_slug:
                continue
            location_name = j.get("label")
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "application/json",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer": "https://www.galerieslafayette.com/m/nos-magasins",
                "Origin": "https://www.galerieslafayette.com",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }

            json_data = {
                "query": "query ($type: String!, $id: String!, $context: ContextInput!) {\n  getPage(type: $type, id: $id, context: $context) {\n    ...Page\n  }\n}\n\nfragment Page on Page {\n  title\n  id\n  errors {\n    ...BusinessFieldError\n  }\n  tagCategories\n  components {\n    name\n    componentId\n    ...HeaderInfoBanner\n    ...SearchNoResult\n    ...CarouselPromo\n    ...DiscountBanner\n    ...EventBanner\n    ...Footer\n    ...Header\n    ...HeroSimple\n    ...Menu\n    ...ProductList\n    ...ProductSheet\n    ...PushCategories\n    ...Reinsurance\n    ...SinglePushEdito\n    ...StoreDetails\n    ...StoreList\n    ...TitleAndCta\n    ...TitleBodyText\n    ...TwoColumnsText\n    ...UniverseNavigation\n  }\n  seo {\n    ...Seo\n  }\n}\n\nfragment CarouselPromo on Component {\n  ... on CarouselPromo {\n    label\n    title\n    text\n    cta {\n      ...Link\n    }\n    cards {\n      image {\n        ...Image\n      }\n      title\n      text\n      cta {\n        ...Link\n      }\n    }\n  }\n}\n\nfragment Image on Image {\n  alt\n  url\n}\n\nfragment Link on Link {\n  label\n  scramble\n  url\n}\n\nfragment DiscountBanner on Component {\n  ... on DiscountBanner {\n    headerText\n    title\n    titleColor\n    codes {\n      text\n      code\n    }\n    ctas {\n      ...Link\n    }\n    textColor\n    backgroundColor\n    legalNotices\n    imageWrapper: backgroundImage {\n      mobile {\n        ...Image\n      }\n      desktop {\n        ...Image\n      }\n    }\n    bannerLink\n  }\n}\n\nfragment Cta on Cta {\n  color\n  link\n  text\n}\n\nfragment EventBanner on Component {\n  ... on EventBanner {\n    type\n    title\n    textColor\n    text\n    backgroundParallax\n    mobileBackgroundImage {\n      ...Image\n    }\n    desktopBackgroundImage {\n      ...Image\n    }\n    backgroundColor\n    mainMedia {\n      ...Image\n    }\n    majorCta {\n      ...Link\n    }\n    minorCtas {\n      ...Link\n    }\n  }\n}\n\nfragment Footer on Component {\n  ... on Footer {\n    legalLinks: legalNotices {\n      ...Link\n    }\n    links {\n      title\n      links {\n        ...Link\n      }\n    }\n    socialNetworks {\n      title\n      subtitle\n      values {\n        id\n        url\n      }\n    }\n  }\n}\n\nfragment Header on Component {\n  ... on Header {\n    searchBar {\n      suggestions {\n        title\n        links {\n          ...Link\n        }\n      }\n      noResult {\n        title\n        message\n        thumbnails {\n          label\n          image {\n            ...Image\n          }\n          targetUrl\n        }\n      }\n    }\n  }\n}\n\nfragment HeroSimple on Component {\n  ... on HeroSimple {\n    label\n    mainTitle: title\n    subTitle\n    fontColor: textColor\n    legalTerms\n    backgroundImage {\n      mobile {\n        ...DetailedImage\n      }\n      desktop {\n        ...DetailedImage\n      }\n    }\n    backgroundVideoId {\n      mobile\n      desktop\n    }\n    backgroundColor\n    links {\n      ...Link\n    }\n    ctaStyle\n    ctaLight\n  }\n}\n\nfragment DetailedImage on DetailedImage {\n  alt\n  url\n  dimensions {\n    width\n    height\n  }\n}\n\nfragment Menu on Component {\n  ... on Menu {\n    universes {\n      title {\n        ...Link\n      }\n      color\n      subUniverses {\n        title {\n          ...Link\n        }\n        categories {\n          title {\n            ...Link\n          }\n          new\n        }\n      }\n      sidebar {\n        title {\n          label\n          name\n          ...Link\n        }\n        categories {\n          title {\n            ...Link\n          }\n        }\n        image {\n          ...Image\n        }\n        imageUrl\n      }\n      disabledDevices\n    }\n  }\n}\n\nfragment ProductList on Component {\n  ... on ProductList {\n    seoPaginationText\n    header {\n      ...HeaderContentBannerEdito\n      ...HeaderContentBannerPromotion\n    }\n  }\n}\n\nfragment HeaderContentBannerEdito on Component {\n  ... on HeaderContentBannerEdito {\n    name\n    richText: text {\n      ...RichText\n    }\n    customColor\n    insideCtaLink {\n      ...Link\n    }\n    links {\n      ...Link\n    }\n    backgroundColor\n    editoImage: image {\n      mobile {\n        ...Image\n      }\n      desktop {\n        ...Image\n      }\n    }\n    legalTerms\n    imagePosition\n  }\n}\n\nfragment RichText on RichText {\n  paragraphs {\n    contents {\n      marks\n      text\n    }\n  }\n}\n\nfragment HeaderContentBannerPromotion on Component {\n  ... on HeaderContentBannerPromotion {\n    name\n    headerText\n    title\n    promoCodes\n    customColor\n    insideCtaLink {\n      ...Link\n    }\n    links {\n      ...Link\n    }\n    backgroundColor\n    promoImage: image {\n      mobile {\n        ...Image\n      }\n      desktop {\n        ...Image\n      }\n    }\n    legalTerms\n    imagePosition\n  }\n}\n\nfragment ProductSheet on ProductSheet {\n  defaultReturnTitle\n  mkpReturnTitle\n  goforgoodText\n}\n\nfragment PushCategories on Component {\n  ... on PushCategories {\n    bannerText\n    categories {\n      label\n      description\n      url\n      image {\n        ...Image\n      }\n    }\n    newsZone {\n      title\n      cta {\n        ...Cta\n      }\n    }\n  }\n}\n\nfragment Reinsurance on Component {\n  ... on Reinsurance {\n    reinsuranceMessages {\n      icon\n      title {\n        label\n        ... on Link {\n          url\n          scramble\n        }\n      }\n      subtitle\n    }\n  }\n}\n\nfragment SinglePushEdito on Component {\n  ... on SinglePushEdito {\n    title\n    subtitle\n    color\n    background\n    banner\n    cta {\n      ...Cta\n    }\n    images {\n      type\n      alt\n      url\n    }\n  }\n}\n\nfragment StoreDetails on Component {\n  ... on StoreDetails {\n    title\n    image {\n      ...DetailedImage\n    }\n    imageDesktop {\n      ...DetailedImage\n    }\n    phone\n    linkToShopMap {\n      ...Link\n    }\n    address\n    complementaryInfo\n    mondayOpeningHours\n    tuesdayOpeningHours\n    wednesdayOpeningHours\n    thursdayOpeningHours\n    fridayOpeningHours\n    saturdayOpeningHours\n    sundayOpeningHours\n  }\n}\n\nfragment StoreList on Component {\n  ... on StoreList {\n    welcomeMessage\n    stores {\n      ...Link\n    }\n  }\n}\n\nfragment TitleBodyText on Component {\n  ... on TitleBodyText {\n    richText {\n      ...RichText\n    }\n    richTitle {\n      ...RichText\n    }\n    richSubtitle {\n      ...RichText\n    }\n    textColor\n    backgroundColor\n  }\n}\n\nfragment TitleAndCta on Component {\n  ... on TitleAndCta {\n    title\n    cta {\n      ...Cta\n    }\n  }\n}\n\nfragment TwoColumnsText on Component {\n  ... on TwoColumnsText {\n    richText {\n      ...RichText\n    }\n    richTitle {\n      ...RichText\n    }\n  }\n}\n\nfragment UniverseNavigation on Component {\n  ... on UniverseNavigation {\n    tagline\n    universes {\n      link {\n        ...Link\n      }\n      images {\n        ...Image\n      }\n    }\n  }\n}\n\nfragment HeaderInfoBanner on Component {\n  ... on HeaderInfoBanner {\n    messagePrimary {\n      desktop {\n        ...RichText\n      }\n      mobile {\n        ...RichText\n      }\n    }\n    messageSecondary {\n      desktop {\n        ...RichText\n      }\n      mobile {\n        ...RichText\n      }\n    }\n    linkPrimary {\n      ...Link\n    }\n    linkSecondary {\n      ...Link\n    }\n    customColor\n    backgroundColor\n  }\n}\n\nfragment BusinessFieldError on BusinessFieldError {\n  causes\n  contentType\n  id\n  name\n  url\n}\n\nfragment Seo on Seo {\n  metaDescription\n  title\n}\n\nfragment SearchNoResult on Component {\n  ... on SearchNoResult {\n    searchCTA: cta\n    searchLabel: label\n    searchDescription: description\n  }\n}\n",
                "variables": {
                    "type": "shop",
                    "id": f"{api_slug}",
                    "context": {
                        "tenant": "gl",
                        "channel": "ecom",
                        "locale": "fr",
                    },
                },
                "cacheData": {
                    "operationName": "page",
                    "context": {
                        "tenant": "gl",
                        "subtenant": "3004",
                        "channel": "ecom",
                        "locale": "fr",
                    },
                    "operationDetails": {
                        "type": "shop",
                        "id": f"{api_slug}",
                    },
                },
            }

            r = session.post("https://www.galerieslafayette.com/api", json=json_data)
            log.info(f"POST Response: {r}")
            js = r.json()["data"]["getPage"]["components"]
            for j in js:
                name = j.get("name")
                if name != "StoreDetails":
                    continue
                ad = "".join(j.get("address")).replace("\r", " ").replace("\n", " ").strip()
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                country_code = "FR"
                city = a.city or "<MISSING>"
                phone = j.get("phone")
                hours_of_operation = (
                    f"{j.get('mondayOpeningHours')} {j.get('tuesdayOpeningHours')} {j.get('wednesdayOpeningHours')} {j.get('thursdayOpeningHours')} {j.get('fridayOpeningHours')} {j.get('saturdayOpeningHours')} {j.get('sundayOpeningHours')}".strip()
                    or "<MISSING>"
                )
                if location_name == "Magasin Galeries Lafayette Bordeaux":
                    street_address = "11-19 rue Sainte Catherine"
                    postal = "33 000"
                    city = "Bordeaux"
                if location_name == "Magasin Galeries Lafayette Luxembourg":
                    city = "LUXEMBOURG"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
