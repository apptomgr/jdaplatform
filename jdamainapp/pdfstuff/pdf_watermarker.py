# pdf_watermarker.py
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
import os

def create_watermark(input_pdf, output, watermark):
    # picture_path ='everest_logo.jpg'
    # text = None #'Made for Everest'
    #
    # #w = watermark.scaleBy(0.5)
    #
    # c = canvas.Canvas(watermark)
    #
    # if picture_path:
    #     c.drawImage(picture_path, 100, 500)
    #
    # if text:
    #     #c.setFontSize(8)
    #     c.setFont('Helvetica-Bold', 14)
    #     c.drawString(45, 20, text)
    #
    # c.save()


    watermark_obj = PdfFileReader(watermark)
    watermark_page = watermark_obj.getPage(0)

    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    # Watermark all the pages
    for page in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page)
        page.mergePage(watermark_page)
        pdf_writer.addPage(page)

    with open(output, 'wb') as out:
        pdf_writer.write(out)

if __name__ == '__main__':
    create_watermark(
        input_pdf='pdf_test_doc.pdf',
        output='watermarked_doc.pdf',
        watermark='everest_logo.pdf')