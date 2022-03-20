import camelot
from sgrequests import SgRequests
import os

os.system("pip install ghostscript python3-tk")

session = SgRequests()
pdf_url = "https://www.bbva.pe/content/dam/public-web/peru/documents/personas/canales-de-atencion/oficinas/Oficinas-BBVA-abiertas-23.10.20.pdf"
pdf_response = session.get(pdf_url)
my_raw_data = pdf_response.content

with open("my_pdf.pdf", "wb") as my_data:
    my_data.write(my_raw_data)

tables = camelot.read_pdf("my_pdf.pdf")
print("Total tables extracted:", tables.n)

print(tables[0].df)