# =========================================================================================#
# OWNER : Aakaash Ramnath Sankar
# DATE : 2020-10-30
# FILE : app.py
# DEVELOPER : Aakaash Ramnath Sankar
# DESCRIPTION : Generate payslips in PDF format using Excel file(s) as an input
# =========================================================================================#

import logging
import datetime
from datetime import datetime, timedelta
from fpdf import FPDF, HTMLMixin

logging.basicConfig(
    format="=>%(levelname)s : %(asctime)s : %(filename)s : %(funcName)s |::| %(message)s",
    level=logging.DEBUG,
)


def get_timestamp_as_str():
    """Fetch current datetimestamp in string

    Returns:
        str: current datetime
    """
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class MyFPDF(FPDF, HTMLMixin):
    """Class to create FPDF & HTMLMixin library objects

    Args:
        FPDF (Library): Object
        HTMLMixin (Library): Object
    """

    FPDF(format="A4")


def get_html_content(path: str):
    """[read the html content from the file to write the pdf]

    Args:
        path (str): [path of the text file containing html content]

    Returns:
        str: [File content (HTML string)]
    """
    try:
        with open(path, "r") as file:
            return file.read()
    # pylint:disable=broad-except
    except Exception as error:
        logging.error(str(error))


def initialize_pdf_template(img_path: str = None):
    """[Create the PDF object & import the background image(optional)]

    Args:
        img_path (str, optional): [path of the image to be made as PDF background]. Defaults to None.

    Returns:
        [MyPDF]: [Class instance]
    """
    try:
        obj = MyFPDF()
        obj.add_page()
        if img_path is not None:
            obj.image(img_path, x=0, y=0, w=210)
        return obj
    # pylint:disable=broad-except
    except Exception as error:
        logging.error(str(error))


pdf_obj = initialize_pdf_template(r"./utility/payslip_bg.png")
pdf_obj.ln(43)
pdf_obj.write_html(get_html_content(r"./utility/details.txt"))
pdf_obj.output("outfile.pdf")


def main():
    """This is the main function

    Returns:
        Boolean: True/False based on execution status
    """
    return True


if __name__ == "__main__":
    print(
        "============== Execution Started  "
        + get_timestamp_as_str()
        + "================\n"
    )

    if main():
        print(
            "\n============== Successfully Ended "
            + get_timestamp_as_str()
            + "================"
        )
