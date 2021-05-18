# compatible with Python versions 2.6, 2.7,
# and 3.2 - 3.5. (pip3 install pypdf4)
from PyPDF4 import PdfFileWriter, PdfFileReader
import PyPDF4
from django.http import FileResponse
from django.conf import settings #or from my_project import settings
import img2pdf
from PIL import Image
from reportlab.pdfgen import canvas
import os

# img2pdf converts curr user profile .png logo to pdf
def img2pdf(img, curr_user):
    #print(f"13: {img}")
    image1 = Image.open(img)
    im1 = image1.convert('RGB')
    im1.save(f"{settings.MEDIA_ROOT}/profile_logo/{curr_user}_watermark.pdf")



def res_tes(input_pdf, output_pdf, watermark):

    #print(f"File input util  orig:{settings.MEDIA_ROOT}/{input_pdf}")
    #print(f"File output util {output_pdf}")
    #print(f"File watermark util {settings.MEDIA_ROOT}/{watermark}")
    #input_pdf=settings.MEDIA_ROOT+'/'+input_pdf

    print(f"input_pdf: {input_pdf}")
    print(f"output_pdf: {output_pdf}")
    print(f"watermark: {watermark}")
    #pdf_reader = PdfFileReader(watermark)

    #print(input_pdf)

    #print(f"24: {settings.MEDIA_ROOT}")

def put_watermark(input_pdf, output_pdf, watermark, logo_img):
    print(f"38: {logo_img}")
    picture_path = logo_img #'everest_logo.jpg'
    text = None #'Produite pour'

    c = canvas.Canvas(watermark)

    if picture_path:
        c.drawImage(picture_path, 450, 560)

    if text:
        c.setFontSize(14)
        c.setFont('Helvetica-Bold', 14)
        c.drawString(45, 20, text)

    c.save()

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


# f = default_storage.open(os.path.join('Data_Files', new_file), 'r')
# data = f.read()
# f.close()
# print(data)

# import PyPDF2
#
# pdf_file = "pdf_test_doc.pdf"
#
# watermark = "everest_logo.pdf"
#
# merged_file = "merged.pdf"
#
# input_file = open(pdf_file,'rb')
# input_pdf = PyPDF2.PdfFileReader(input_file)
#
# watermark_file = open(watermark,'rb')
# watermark_pdf = PyPDF2.PdfFileReader(watermark_file)
#
# pdf_page = input_pdf.getPage(0)
#
# watermark_page = watermark_pdf.getPage(0)
#
# pdf_page.mergePage(watermark_page)
#
# output = PyPDF2.PdfFileWriter()
#
# output.addPage(pdf_page)
#
# merged_file = open(merged_file,'wb')
# output.write(merged_file)
#
# merged_file.close()
# watermark_file.close()
# input_file.close()

