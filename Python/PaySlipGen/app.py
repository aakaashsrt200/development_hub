# =========================================================================================#
# OWNER : Aakaash Ramnath Sankar
# DATE : 2020-10-30
# FILE : app.py
# DEVELOPER : Aakaash Ramnath Sankar
# DESCRIPTION : Generate payslips in PDF format using Excel file(s) as an input
# =========================================================================================#

import os
import sys
import logging
import datetime
from datetime import datetime, timedelta
from fpdf import FPDF, HTMLMixin
import pandas as pd
import pathlib
import email as mail
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# PROGRAM CONSTANTS
CONST_PROGRAM_FAILURE = 0
CONST_PROGRAM_SUCCESS = 1

logging.basicConfig(
    format="=>%(levelname)s : %(asctime)s : %(filename)s : %(funcName)s |::| %(message)s",
    level=logging.DEBUG,
)

MONTH_LIST = [
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
    "JAN",
    "FEB",
    "MAR",
]
CURRENT_YEAR = 2020
CURRENT_MONTH = "NOV"
SOURCE_FILES_PATH = "./files/"
SENDER_EMAIL = "aakaashsrt200@gmail.com"
PASSWORD = "varaak~260116"


def get_timestamp_as_str():
    """Fetch current datetimestamp in string

    Returns:
        str: current datetime
    """
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_directory(folder_path):
    """
    Makes sure that the given folder location is available or creates one

    Args :
        folder_path (str) : path to check
    """
    try:
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error("*** " + "Couldn't create folder : " + folder_path)
        logging.error("*** " + str(e))


def send_email(recepient, attachment):
    """
    Send email to the given recepient & attachment

    Args :
        recepient (str) : email ID to which payslip has to be sent
        attachment (str) : path of the payslip
    """
    logging.debug(recepient)
    logging.debug(attachment)

    email_body = (
        "Here is the payslip for the month of "
        + str(CURRENT_MONTH)
        + "-"
        + str(CURRENT_YEAR)
    )
    subject = (
        "Accounts Dept | Payslip -  " + str(CURRENT_MONTH) + "-" + str(CURRENT_YEAR)
    )
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recepient
    message["Subject"] = subject
    message["Bcc"] = ""

    # Add body to email
    message.attach(MIMEText(email_body, "plain"))

    attach_file_path = open(attachment, "rb")  # Open the file as binary mode
    payload = MIMEBase("application", "octate-stream")
    payload.set_payload((attach_file_path).read())
    encoders.encode_base64(payload)  # encode the attachment
    # add payload header with filename
    payload.add_header(
        "Content-Disposition", "attachment", filename=attachment.split("/")[-1]
    )
    message.attach(payload)

    text = message.as_string()

    session = smtplib.SMTP("smtp.gmail.com", 587)  # use gmail with port
    session.starttls()
    session.login(SENDER_EMAIL, PASSWORD)
    session.sendmail(SENDER_EMAIL, recepient, text)


def read_excel(file_name: str, **kwargs):
    """Write the given HTML content to the PDF object & then to the file

    Args:
        filename (str): Pre-defined PDF object to which the THML content has to be written
        **kwargs (str) : Any relative parameters to be passed while reading the excel file using Pandas libary can be passed

    Returns:
        (Datafrme) : Returns Excel dataframe
    """
    return pd.read_excel(file_name, **kwargs)


def file_list(path, extension: str = ".xlsx"):
    """Get the list of files in a given folder with given extension (By default takes .xlsx as extension value)

    Args:
        path (str): Path in which file list has to be retrieved
        extension (str) : Any extension filter to be applied on the list of files (Default .xlsx)

    Returns:
        filelist (list) : List of files in the folder that matches the extension condition
    """

    filelist = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.lower().endswith(extension.lower()):
                split_name = filename.split(sep="_")
                if len(split_name) == 2 and split_name[0] in MONTH_LIST:
                    split_name = split_name[1].split(sep=".")
                    if len(split_name) and split_name[0].isnumeric():
                        filelist.append(filename)
    return filelist


def build_employee_data(employee_df, ytd_dataframe, eligible_months):
    """Produce the data related to an employee (both YTD & Current month)

    Args:
        employee_df (DataFrame): Has current month data
        ytd_dataframe (DataFrame) : Has YTD data
        eligible_months (list) : Has the list of months with which YTD has been calculated

    Returns:
        result (Dict) : Dict with all employee related data filled in
    """

    employee_df = employee_df.fillna(0).to_dict(orient="records")[0]
    numerical_column = [
        "FIXED SALARY",
        "A.DAYS",
        "W.DAYS",
        "BASIC",
        "DA",
        "OTHR ALLOW",
        "HRA",
        "EARNED SALARY",
        "EPFO SALARY",
        "O T DAYS",
        "O.T WAGES",
        "ANY ADDITONAL (NO ESI EFFECT)",
        "GROSS SALARY",
        "EPFO",
        "ESIC",
        "TDS",
        "Transport",
        "Adavance",
        "Total Teduction",
        "Net salary ",
        "TOTAL CHK",
    ]
    ytd_data = ytd_dataframe.copy()
    ytd_data = ytd_data[(ytd_data["EMP ID"] == "10001")]
    ytd_data["MONTH YEAR"] = ytd_data[["MONTH", "YEAR"]].apply(
        lambda x: "_".join(x), axis=1
    )
    ytd_data = ytd_data[ytd_data["MONTH YEAR"].isin(eligible_months)]
    ytd_data = ytd_data[["EMP ID"] + numerical_column]
    ytd_data = ytd_data.apply(pd.to_numeric, errors="coerce").fillna(0)
    ytd_data = ytd_data.groupby(["EMP ID"]).sum()
    ytd_data.reset_index(inplace=True)
    ytd_data = ytd_data.to_dict(orient="records")[0]
    result = {"YTD " + key: val for key, val in ytd_data.items()}
    result.update(employee_df)
    return result


def write_pdf(pdf, html, filename):
    """Write the given HTML content to the PDF object & then to the file

    Args:
        pdf (obj): Pre-defined PDF object to which the THML content has to be written
        html (str) : HTML taglines in string format
        filename (str) : Output file name
    """
    path = "./payslip/"
    ensure_directory(path)
    pdf.write_html(html)
    pdf.output(path + filename)


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
        logging.error("*** " + str(error))


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
        logging.error("*** " + str(error))


def process(pdf, html):
    """Process orchestrator takes control of the procedure

    Args:
        pdf (obj): Pre-defined PDF object to which the THML content has to be written
        html (str) : HTML taglines in string format

    Return:
        (Bool): Says the status of the function run
    """
    try:
        obj = pdf
        available_files = file_list(SOURCE_FILES_PATH)
        index = MONTH_LIST.index(CURRENT_MONTH)
        ellgible_files = []
        if index < 9:
            for i, m in enumerate(MONTH_LIST):
                if i > 8:
                    pass
                else:
                    if i <= index:
                        ellgible_files.append(m + "_" + str(CURRENT_YEAR) + ".xlsx")
        else:
            for i, m in enumerate(MONTH_LIST):
                if i < 9:
                    ellgible_files.append(m + "_" + str(CURRENT_YEAR - 1) + ".xlsx")
                else:
                    if i <= index:
                        ellgible_files.append(m + "_" + str(CURRENT_YEAR) + ".xlsx")

        if not set(ellgible_files).issubset(set(available_files)):
            missing_files = [
                ellgible_file
                for ellgible_file in ellgible_files
                if not ellgible_file in available_files
            ]
            logging.warning("REQUIRED FILES NOT FOUNT")
            logging.error("*** " + "MISSING FILES : " + str(missing_files))
            return False

        data_frames = []
        eligible_months = [file.replace(".xlsx", "") for file in ellgible_files]
        # Append dataframes of all the months
        for file in ellgible_files:
            data = read_excel(
                f"{SOURCE_FILES_PATH}{file}", sheet_name=0, header=0, skiprows=1
            )
            cols = data.columns
            conv = dict(zip(cols, [str] * len(cols)))
            data = read_excel(
                f"{SOURCE_FILES_PATH}{file}",
                sheet_name=0,
                header=0,
                skiprows=1,
                converters=conv,
            )
            data.dropna(axis=0, how="all", inplace=True)
            data_frames.append(data)

        ytd_dataframe = pd.concat(data_frames)
        ytd_dataframe = ytd_dataframe.dropna(subset=["EMP ID", "EMPLOYEE  NAME"])

        current_month_data = ytd_dataframe.copy()
        current_month_data = current_month_data[
            (current_month_data["MONTH"] == CURRENT_MONTH)
            & (current_month_data["YEAR"] == str(CURRENT_YEAR))
        ]

        employee_list = current_month_data["EMP ID"].unique()
        # Building the necessary data for individual employee
        for employee in employee_list:
            logging.debug("Generating Payslip for employee ID : " + employee)
            employee_df = current_month_data[current_month_data["EMP ID"] == employee]
            data = build_employee_data(employee_df, ytd_dataframe, eligible_months)
            """
                Call the function to replace the strings from HTML content & write the HTML data into PDF
            """
            write_pdf(pdf=pdf, html=html, filename=employee + ".pdf")
            payslip_path = os.getcwd() + "/payslip/" + employee + ".pdf"
            # send_email(data["EMAIL_ID"], payslip_path)
        return True
    except Exception as e:
        logging.error("*** " + str(e))
        return False


def main():
    """This is the main function

    Returns:
        Boolean: True/False based on execution status
    """
    pdf = initialize_pdf_template()
    # pdf = initialize_pdf_template(r"./utility/payslip_bg.png")
    html = get_html_content(r"./utility/details.txt")
    pdf.ln(43)
    process_status = process(pdf, html)

    if not process_status:
        # To be built
        logging.error("*** " + "Error in process function")
        sys.exit(CONST_PROGRAM_FAILURE)
    else:
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
        sys.exit(CONST_PROGRAM_SUCCESS)
