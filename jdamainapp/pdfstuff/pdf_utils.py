from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
import os
"""
Refer to an image if you want to add an image to a watermark.
Fill in text if you want to watermark with text.
Alternatively, following settings will skip this.
picture_path = None
text = None
"""
picture_path = 'everest_logo.jpg'
text = 'EVEREST'

# Folder in which PDF files will be watermarked. (Could be shared folder)
folder_path = '.'
c = canvas.Canvas('watermark.pdf')

if picture_path:
    c.drawImage(picture_path, 15, 15)

if text:
    c.setFontSize(22)
    c.setFont('Helvetica-Bold', 36)
    c.drawString(15, 15,text)

c.save()
watermark = PdfFileReader(open("watermark.pdf", "rb"))

for file in os.listdir(folder_path):
    if file.endswith(".pdf"):
        output_file = PdfFileWriter()
        input_file = PdfFileReader(open(folder_path + '/'+ file, "rb"))
        page_count = input_file.getNumPages()

for page_number in range(page_count):
    input_page = input_file.getPage(page_number)
    input_page.mergePage(watermark.getPage(0))
    output_file.addPage(input_page)


output_path = folder_path + '/'+ file.split('.pdf')[0] + '_watermarked' + '.pdf'
with open(output_path, "wb") as outputStream:
   output_file.write(outputStream)