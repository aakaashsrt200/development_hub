# =========================================================================================#
# OWNER : Aakaash Ramnath Sankar
# DATE : 2020-10-30
# FILE : app.py
# DEVELOPER : Aakaash Ramnath Sankar
# DESCRIPTION : Generate payslips in PDF format using Excel file(s) as an input
# =========================================================================================#

import os
import sys
import re
import logging
import datetime
from datetime import datetime, timedelta
from fpdf import FPDF, HTMLMixin
import pandas as pd
from num2words import num2words
import pathlib
import email as mail
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import pikepdf
from pikepdf import Pdf
import numpy as np

# PROGRAM CONSTANTS
CONST_PROGRAM_FAILURE = 0
CONST_PROGRAM_SUCCESS = 1


def get_timestamp_as_str():
    """Fetch current datetimestamp in string

    Returns:
        str: current datetime
    """
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


CONST_OUTPUT_PATH = (
    "./payslip/" + get_timestamp_as_str().replace("-", "").replace(":", "")[0:13] + r"/"
)
CONST_SOURCE_FILES_PATH = r"./files/"
CONST_CONFIG_PATH = r"./config.ini"
CONST_BG_IMAGE_PATH = r"./utility/payslip_bg.png"

logging.basicConfig(
    format="=>%(levelname)s : %(asctime)s : %(filename)s : %(funcName)s |::| %(message)s",
    level=logging.DEBUG,
)


def get_config_value(path):
    """
    Connect to conf.ini and get the values

    Args :
        path (str) : path of the config .ini file

    Returns:
        config_data (obj) : Object that contains all the config data in it
    """
    config_data = configparser.ConfigParser()
    config_path = path
    config_data.read(config_path)
    # data = appConfig.get(key, value)
    return config_data


config = get_config_value(CONST_CONFIG_PATH)

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
CURRENT_YEAR = int(config.get("run_config", "for_the_year"))
CURRENT_MONTH = config.get("run_config", "for_the_month").upper()
EMAIL_FLAG = (
    True if config.get("email_config", "email_send").lower() == "true" else False
)
SENDER_EMAIL = config.get("email_config", "email_address")
PASSWORD = config.get("email_config", "email_password")


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


def pdf_protect(attachment, password):
    """
    This function takes a file as an input and creates another file in the same destination
    This file is encrypted with the password defined earlier
    """
    pdf = Pdf.open(attachment, allow_overwriting_input=True)
    pdf.save(
        attachment,
        encryption=pikepdf.Encryption(owner=password, user=password, R=4),
    )
    # you can change the 4 to 6 for 256 aes encryption but that file won't open on Acrobat versions lower than 10.0
    pdf.close()
    return


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


def number_to_words(number):
    try:
        float(number)
        split = str(number).split(".")
        rupees = split[0]
        rupees = (
            num2words(rupees, lang="en_IN").replace("-", " ").replace(",", " ").title()
        )
        paise = ""
        if len(split) > 1:
            paise = split[1][:2]
            if int(paise) > 0:
                paise = (
                    num2words(paise, lang="en_IN")
                    .replace("-", " ")
                    .replace(",", " ")
                    .title()
                )
                return f"Rupees {rupees} & Paise {paise} Only"
        return f"Rupees {rupees} Only"
    except Exception as error:
        return ""


def build_employee_data(employee_df, ytd_dataframe, eligible_months):
    """Produce the data related to an employee (both YTD & Current month)

    Args:
        employee_df (DataFrame): Has current month data
        ytd_dataframe (DataFrame) : Has YTD data
        eligible_months (list) : Has the list of months with which YTD has been calculated

    Returns:
        result (Dict) : Dict with all employee related data filled in
    """
    numerical_column = [
        "FIXED SALARY",
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
    employee_df = employee_df.fillna(0)
    employee_df["GROSS DEDUCTION"] = employee_df.apply(
        lambda row: float(row["EPFO"])
        + float(row["ESIC"])
        + float(row["TDS"])
        + float(row["Transport"])
        + float(row.get("advance", "0")),
        axis=1,
    )
    employee_df[numerical_column] = employee_df[numerical_column].apply(
        pd.to_numeric, errors="coerce", downcast="float"
    )
    employee_df = employee_df.fillna(0)
    employee_df["NET PAY IN WORDS"] = employee_df.apply(
        lambda row: number_to_words(row["Net salary "]), axis=1
    )
    employee_df = employee_df.to_dict(orient="records")[0]
    ytd_data = ytd_dataframe.copy()
    ytd_data["MONTH YEAR"] = ytd_data[["MONTH", "YEAR"]].apply(
        lambda x: "_".join(x), axis=1
    )
    ytd_data = ytd_data[ytd_data["MONTH YEAR"].isin(eligible_months)]
    ytd_data = ytd_data[["EMP ID"] + numerical_column]
    ytd_data = ytd_data.apply(pd.to_numeric, errors="coerce", downcast="float")
    ytd_data = ytd_data.fillna(0)
    ytd_data["GROSS DEDUCTION"] = ytd_data.apply(
        lambda row: float(row["EPFO"])
        + float(row["ESIC"])
        + float(row["TDS"])
        + float(row["Transport"])
        + float(row.get("advance", "0")),
        axis=1,
    )
    ytd_data = ytd_data.groupby(["EMP ID"]).sum()
    ytd_data.reset_index(inplace=True)
    ytd_data = ytd_data.to_dict(orient="records")[0]
    result = {
        "YTD " + key: val and val for key, val in ytd_data.items() if key != "EMP ID"
    }
    result.update(employee_df)
    result.update({"YTD NET PAY IN WORDS": number_to_words(result["YTD Net salary "])})
    for key, value in result.items():
        if isinstance(value, float):
            result[key] = "{:.2f}".format(value)
    return result


def write_pdf(html, filename, password=None):
    """Write the given HTML content to the PDF object & then to the file

    Args:
        pdf (obj): Pre-defined PDF object to which the THML content has to be written
        html (str) : HTML taglines in string format
        filename (str) : Output file name
    """
    # pdf = initialize_pdf_template(CONST_BG_IMAGE_PATH)
    pdf = initialize_pdf_template()
    pdf.ln(43)
    ensure_directory(CONST_OUTPUT_PATH)
    pdf.write_html(html)
    pdf.output(CONST_OUTPUT_PATH + filename)

    if password:
        pdf_protect(CONST_OUTPUT_PATH + filename, password)


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


def replace_place_holders(html: str = "", data: dict = {}):
    """Replace all the place holders in the provided html string

    Args:
        html (str, optional): Html template string. Defaults to "".
        data (dict, optional): Data to be replaced with. Defaults to {}.

    Returns:
        [str]: Html string replaced with placeholders.
    """
    # for key, value in data.items():
    #    html = html.replace("{" + str(key) + "}", str(value))
    pattern = re.compile(r"{[a-zA-Z0-9_/. ]+}")
    match = pattern.findall(html)
    for value in match:
        html = html.replace(
            str(value), str(data.get(str(value).replace("{", "").replace("}", ""), "-"))
        )
        # html = html.replace(value, " - ")
    return html


def process():
    """Process orchestrator takes control of the procedure

    Args:
        pdf (obj): Pre-defined PDF object to which the THML content has to be written
        html (str) : HTML taglines in string format

    Return:
        (Bool): Says the status of the function run
    """
    try:
        available_files = file_list(CONST_SOURCE_FILES_PATH)
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
                f"{CONST_SOURCE_FILES_PATH}{file}",
                sheet_name="MAIN SHEET",
                header=0,
                skiprows=1,
            )
            cols = data.columns
            conv = dict(zip(cols, [str] * len(cols)))
            data = read_excel(
                f"{CONST_SOURCE_FILES_PATH}{file}",
                sheet_name="MAIN SHEET",
                header=0,
                skiprows=1,
                converters=conv,
            )
            data.dropna(axis=0, how="all", inplace=True)
            data_frames.append(data)

        consolidated_data = pd.concat(data_frames)
        current_month_data = consolidated_data.copy()
        current_month_data.to_excel("test.xlsx")
        current_month_data = current_month_data[
            (current_month_data["MONTH"] == CURRENT_MONTH)
            & (current_month_data["YEAR"] == str(CURRENT_YEAR))
        ]
        current_month_data = current_month_data.dropna(subset=["EMP ID"])
        employee_list = current_month_data["EMP ID"].unique()
        # Building the necessary data for individual employee
        for employee in employee_list:
            logging.debug("Generating Payslip for employee ID : " + str(employee))
            employee_df = current_month_data.copy()
            employee_df = current_month_data[current_month_data["EMP ID"] == employee]
            ytd_employee_df = consolidated_data.copy()
            ytd_employee_df = consolidated_data[consolidated_data["EMP ID"] == employee]
            data = build_employee_data(employee_df, ytd_employee_df, eligible_months)
            html = get_html_content(r"./utility/details.txt")
            content = replace_place_holders(html, data)
            write_pdf(
                html=content,
                filename=employee
                + "_"
                + str(CURRENT_MONTH)
                + str(CURRENT_YEAR)
                + ".pdf",
                password=data.get("password", None),
            )
            if EMAIL_FLAG == True:
                payslip_path = (
                    CONST_OUTPUT_PATH
                    + employee
                    + "_"
                    + str(CURRENT_MONTH)
                    + str(CURRENT_YEAR)
                    + ".pdf"
                )
                send_email(data["EMAIL_ID"], payslip_path)
        return True
    except Exception as e:
        logging.error("*** " + str(e))
        return False


def main():
    """This is the main function

    Returns:
        Boolean: True/False based on execution status
    """
    process_status = process()

    if not process_status:
        # To be built
        logging.error("*** " + "Error in process function")
        sys.exit(CONST_PROGRAM_FAILURE)
    else:
        return True


if __name__ == "__main__":
    print(
        "============== Execution Started "
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
