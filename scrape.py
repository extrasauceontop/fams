from dataclasses import dataclass
import tabula
from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
import PyPDF2  # noqa


def get_data():
    x = -1
    while True:
        x = x+1
        session = SgRequests()
        pdf_url = "https://www.bbva.pe/content/dam/public-web/peru/documents/personas/canales-de-atencion/oficinas/Oficinas-BBVA-abiertas-23.10.20.pdf"
        pdf_response = session.get(pdf_url)
        my_raw_data = pdf_response.content

        with open("my_pdf.pdf", "wb") as my_data:
            my_data.write(my_raw_data)
        
        open_pdf_file = open("my_pdf.pdf", "rb")
        read_pdf = PyPDF2.PdfFileReader(open_pdf_file)

        try:
            final_text = ((read_pdf.getPage(x).extractText()))
        except Exception:
            return
        begin_hours = 0
        hours = ""
        for line in final_text.split("\n"):
            if begin_hours == 1:
                hours = hours + line + ", "

            if " mayor parte de nuestra red de oficinas" in line:
                begin_hours = 1
        hours = hours.strip()[:-3]

        df = tabula.read_pdf("my_pdf.pdf", pages='all')[x]
        df = df.fillna("0")

        master_list = df.values.tolist()

        tot_with_0 = 0
        for row in master_list:
            if "0" in row and len(row) == 5:
                tot_with_0 = tot_with_0 + 1
        print(len(master_list))
        print(tot_with_0)

        if len(master_list) == tot_with_0:
            index_0 = True
            index_1 = True
            index_2 = True
            index_3 = True
            index_4 = True
            for row in master_list:
                if row[0] != "0":
                    index_0 = False
                
                if row[1] != "0":
                    index_1 = False
                
                if row[2] != "0":
                    index_2 = False
                
                if row[3] != "0":
                    index_3 = False
                
                if row[4] != "0":
                    index_4 = False
                
            if index_0 == True:
                bad_index = 0

            if index_1 == True:
                bad_index = 1

            if index_2 == True:
                bad_index = 2

            if index_3 == True:
                bad_index = 3

            if index_4 == True:
                bad_index = 4
            
            list_to_iter = []
            for row in master_list:
                list_to_iter.append(row[:bad_index] + row[bad_index+1:])

        else:
            list_to_iter = master_list
            
        index = 0
        no_scrape = -1
        final_list = []
        for row in list_to_iter:
            if no_scrape >= index:
                pass

            elif "0" in row:
                print(row)
                print(x)
                cell_1 = (list_to_iter[index][0] + list_to_iter[index+1][0] + list_to_iter[index+2][0]).replace("0", "").strip()
                cell_2 = (list_to_iter[index][1] + list_to_iter[index+1][1] + list_to_iter[index+2][1]).replace("0", "").strip()
                cell_3 = (list_to_iter[index][2] + list_to_iter[index+1][2] + list_to_iter[index+2][2]).replace("0", "").strip()
                cell_4 = (list_to_iter[index][3] + list_to_iter[index+1][3] + list_to_iter[index+2][3]).replace("0", "").strip()
                
                final_list.append([cell_1, cell_2, cell_3, cell_4])
                no_scrape = index+2
            elif "0" not in row:
                final_list.append(row)
            
            index = index + 1

        for row in final_list:
            locator_domain = "bbva.pe"
            page_url = "https://www.bbva.pe/content/dam/public-web/peru/documents/personas/canales-de-atencion/oficinas/Oficinas-BBVA-abiertas-23.10.20.pdf"
            location_name = row[0]
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            city = row[2]
            store_number = "<MISSING>"
            address = row[1]
            state = row[3]
            zipp = "<MISSING>"
            phone = "<MISSING>"
            location_type = "office"
            country_code = "Peru"

            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
                "country_code": country_code,
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
        ),
        city=sp.MappingField(
            mapping=["city"], is_required=False
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], is_required=False
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
