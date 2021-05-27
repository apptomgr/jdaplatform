# compatible with Python versions 2.6, 2.7,
# and 3.2 - 3.5. (pip3 install pypdf4)
from PyPDF4 import PdfFileWriter, PdfFileReader
import PyPDF4
from django.http import FileResponse
from django.conf import settings #or from my_project import settings
from PIL import Image
from jdapublicationsapp.models import PubTempModel
import fitz
from django.core.files.base import ContentFile
import os
# from django.core.files.storage import default_storage
#
#
# def read_media_file():
#     f = default_storage.open(os.path.join('data_files', new_file), 'r')

def fitz_pdf(pdf_doc, logo, pdf_out):
    #print(f"14: Inside fitz_pdf: pdf_doc: {pdf_doc} - logo: {logo} - pdf_out: {pdf_out}")
    doc =fitz.open(pdf_doc)

    #print(f"18: {os.path.join()}")
    rect = fitz.Rect(320, 10, 360, 50)
    #rect =fitz.Rect(0, 10, 700, 60)
    text = "Intended\nfor"
    #text = "Preparer\npour"
    where = fitz.Point(270, 30) # (x,y)

    for page in doc:
         page.insertImage(rect, filename=logo)
         page.insertText(where, text,
                         fontsize=10,  # default
                         rotate=0,  # rotate text
                         color=(1, 1, 1),  # some color (beige)
                         overlay=True)  # text in foreground


    doc.save(pdf_out)



# img2pdf converts curr user profile .png logo to pdf
def img2pdf(img, curr_user):
    #print(f"13: {img}")
    image1 = Image.open(img)
    im1 = image1.convert('RGB')
    im1.save(f"{settings.MEDIA_ROOT}/profile_logo/{curr_user}_watermark.pdf")



def put_watermark(input_pdf, output_pdf, watermark): # , logo_img):
    # print(f"38: {logo_img}")
    # picture_path = logo_img #'everest_logo.jpg'
    # text = None #'Produite pour'
    #
    # c = canvas.Canvas(watermark)
    #
    # if picture_path:
    #     c.drawImage(picture_path, 420, 560)
    #
    # if text:
    #     c.setFontSize(14)
    #     c.setFont('Helvetica-Bold', 14)
    #     c.drawString(45, 20, text)
    #
    # c.save()

    # reads the watermark pdf file through
    # PdfFileReader
    watermark_instance = PdfFileReader(watermark)

    # fetches the respective page of
    # watermark(1st page)
    watermark_page = watermark_instance.getPage(0)

    # reads the input pdf file
    pdf_reader = PdfFileReader(input_pdf)

    # It creates a pdf writer object for the
    # output file
    pdf_writer = PdfFileWriter()

    # iterates through the original pdf to
    # merge watermarks
    for page in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page)

        # will overlay the watermark_page on top
        # of the current page.
        page.mergePage(watermark_page)

        # add that newly merged page to the
        # pdf_writer object.
        pdf_writer.addPage(page)

    with open(output_pdf, 'wb') as out:
        # writes to the respective output_pdf provided
        pdf_writer.write(out)




def send_file(response, filename):

    img = open(filename, 'rb')
    response = FileResponse(img)

    return response


if __name__ == "__main__":
    pass
    # img_orgl =f"{settings.MEDIA_ROOT}/publications/2021/05/Feb_May.pdf"
    # watermark_photo(img_orgl)
    # put_watermark(
    #     input_pdf='pdf_test_doc.pdf',  # the original pdf
    #     output_pdf='watermark_added1.pdf',  # the modified pdf with watermark
    #     watermark='everest_logo.pdf'  # the watermark to be provided
    # )



