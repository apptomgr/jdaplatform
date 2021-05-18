# compatible with Python versions 2.6, 2.7,
# and 3.2 - 3.5. (pip3 install pypdf4)
from PyPDF4 import PdfFileWriter, PdfFileReader
import PyPDF4

#PyPDF4.PdfFileReader('pdf_test_doc.pdf')

def res_tes():
    pass

def put_watermark(input_pdf, output_pdf, watermark):
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
    put_watermark(
        input_pdf='pdf_test_doc.pdf',  # the original pdf
        output_pdf='watermark_added1.pdf',  # the modified pdf with watermark
        watermark='everest_logo.pdf'  # the watermark to be provided
    )




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

