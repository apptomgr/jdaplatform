# compatible with Python versions 2.6, 2.7,
# and 3.2 - 3.5. (pip3 install pypdf4)
from PyPDF4 import PdfFileWriter, PdfFileReader
#import PyPDF4
import fitz

#PyPDF4.PdfFileReader('pdf_test_doc.pdf')


def fitz_pdf():
    print('testing fitz_pdf')
    doc =fitz.open("SONATEL_2021.pdf")

    rect =fitz.Rect(0, 10, 700, 60)
    fname = "F0"
    text = "Intended\nfor"
    #text = "Preparer\npour"
    where = fitz.Point(270, 30) # (x,y)


    for page in doc:
         page.insertImage(rect, filename='everest_logo.jpg')
         page.insertText(where, text,
                         fontsize=12,  # default
                         rotate=0,  # rotate text
                         color=(1, 1, 1),  # some color (blue)
                         overlay=True)  # text in foreground


    doc.save('fitz_out.pdf')
    #doc.write('fitz_out.pdf')



def fitz_pdf_2():
    doc = fitz.open("SONATEL_2021.pdf")
    w = 300
    h = 300
    img = open("everest_logo.jpg", "rb").read()
    rect = fitz.Rect(100, 200, w, h)

    for i in range(0, doc.pageCount):
        page = doc[i]
        page.insertImage(rect, stream=img)

    doc.save('fitz_out.pdf')

def res_tes():
    pass

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





if __name__ == "__main__":
    fitz_pdf()
    # put_watermark(
    #     input_pdf='pdf_test_doc.pdf',  # the original pdf
    #     output_pdf='watermark_added1.pdf',  # the modified pdf with watermark
    #     watermark='everest_logo.pdf'  # the watermark to be provided
    # )




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

