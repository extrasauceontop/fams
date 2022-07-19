# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import ssl
import pandas as pd

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    start_urls = {
        "https://www.sony.com.ar/corporate/AR/dondecomprar/dondecomprar.html": "https://www.sony.com.ar/corporate/AR/dondecomprar/data/AR_Stores.xls",
        "https://www.sony.co.cr/corporate/CR/dondecomprar/dondecomprar.html": "https://www.sony.co.cr/corporate/CR/dondecomprar/data/CR_Stores.xls",
        "https://www.sony.com.mx/corporate/MX/dondecomprar/dondecomprar.html": "https://www.sony.com.mx/corporate/MX/dondecomprar/data/MX_Stores.xlsx",
        "https://www.sony.com.do/corporate/DO/dondecomprar/dondecomprar.html": "https://www.sony.com.do/corporate/DO/dondecomprar/data/DO_Stores.xlsx",
        "https://www.sony.com.bo/corporate/BO/dondecomprar/dondecomprar.html": "https://www.sony.com.bo/corporate/BO/dondecomprar/data/BO_Stores.xls",
        "https://www.sony.com.ec/corporate/EC/dondecomprar/dondecomprar.html": "https://www.sony.com.ec/corporate/EC/dondecomprar/data/EC_Stores.xls",
        "https://www.sony.com.ni/corporate/NI/dondecomprar/dondecomprar.html": "https://www.sony.com.ni/corporate/NI/dondecomprar/data/NI_Stores.xlsx",
        "https://www.sony.com.sv/corporate/SV/dondecomprar/dondecomprar.html": "https://www.sony.com.sv/corporate/SV/dondecomprar/data/SV_Stores.xls",
        "https://www.sony.com.pa/corporate/PA/dondecomprar/dondecomprar.html": "https://www.sony.com.pa/corporate/PA/dondecomprar/data/PA_Stores.xls",
        "https://www.sony.cl/corporate/CL/dondecomprar/dondecomprar.html": "https://www.sony.cl/corporate/CL/dondecomprar/data/CL_Stores.xls",
        "https://www.sony.com.gt/corporate/GT/dondecomprar/dondecomprar.html": "https://www.sony.com.gt/corporate/GT/dondecomprar/data/GT_Stores.xls",
        "https://www.sony.com.pe/corporate/PE/dondecomprar/dondecomprar.html": "https://www.sony.com.pe/corporate/PE/dondecomprar/data/PE_Stores.xlsx",
        "https://www.sony.com.co/corporate/CO/dondecomprar/dondecomprar.html": "https://www.sony.com.co/corporate/CO/dondecomprar/data/CO_Stores.xls",
        "https://www.sony.com.hn/corporate/HN/dondecomprar/dondecomprar.html": "https://www.sony.com.hn/corporate/HN/dondecomprar/data/HN_Stores.xls",
    }
    domain = "sony-lain.com"

    for page_url, data_url in start_urls.items():
        try:
            df = pd.read_excel(data_url)
        except Exception:
            df = pd.read_excel(data_url, engine='openpyxl')
        for index, poi in df.iterrows():
            phone = ""
            if type(poi["phone"]) != float:
                phone = str(poi["phone"]).split(",")[0]
            print(poi["name"])
            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"],
                city=poi["city"],
                state=poi["region"],
                zip_postal="",
                country_code=page_url.split("/")[4],
                store_number=index,
                phone=phone,
                location_type=poi["type"],
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation="",
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
