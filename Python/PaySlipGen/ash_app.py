import os

import pandas as pd
import numpy as np

MONTH_LIST = ["APR", "MAY", "JUN", "JUL", "AUG", "SEP",
              "OCT", "NOV", "DEC", "JAN", "FEB", "MAR"]

SOURCE_FILES_PATH = "./src/files/"


def read_excel(file_name: str, **kwargs):
    return pd.read_excel(file_name, **kwargs)


def fileList(path, extension: str = ".xlsx"):
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


available_files = fileList(SOURCE_FILES_PATH)
current_year = 2020
current_month = "NOV"


def run():

    index = MONTH_LIST.index(current_month)
    ellgible_files = []
    if index < 9:
        for i, m in enumerate(MONTH_LIST):
            if i > 8:
                pass
            else:
                if i <= index:
                    ellgible_files.append(m+"_"+str(current_year)+".xlsx")
    else:
        for i, m in enumerate(MONTH_LIST):
            if i < 9:
                ellgible_files.append(m+"_"+str(current_year-1)+".xlsx")
            else:
                if i <= index:
                    ellgible_files.append(m+"_"+str(current_year)+".xlsx")

    if not set(ellgible_files).issubset(set(available_files)):
        missing_files = [
            ellgible_file for ellgible_file in ellgible_files if not ellgible_file in available_files]
        print("REQUIRED FILES NOT FOUNT")
        print("MISSING FILES : "+str(missing_files))
        return None

    data_frames = []
    elligible_months = [file.replace(".xlsx", "") for file in ellgible_files]
    for file in ellgible_files:
        data = read_excel(f"{SOURCE_FILES_PATH}{file}", sheet_name=0,
                          header=0, skiprows=1)
        cols = data.columns
        conv = dict(zip(cols, [str] * len(cols)))
        data = read_excel(f"{SOURCE_FILES_PATH}{file}", sheet_name=0,
                          header=0, skiprows=1, converters=conv)
        data.dropna(
            axis=0,
            how="all",
            inplace=True
        )
        data_frames.append(data)

    result_dataframe = pd.concat(data_frames)
    current_month_data = result_dataframe.copy()

    current_month_data = current_month_data[(current_month_data["EMP ID"] == "10001")
                                            & (current_month_data["MONTH"] == current_month) & (current_month_data["YEAR"] == str(current_year))]
    current_month_data = current_month_data.fillna(
        0).to_dict(orient="records")[0]
    numerical_column = ["FIXED SALARY", "A.DAYS", "W.DAYS", "BASIC", "DA",
                        "OTHR ALLOW", "HRA", "EARNED SALARY", "EPFO SALARY", "O T DAYS",
                        "O.T WAGES", "ANY ADDITONAL (NO ESI EFFECT)", "GROSS SALARY", "EPFO",
                        "ESIC", "TDS", "Transport", "Adavance", "Total Teduction",
                        "Net salary ", "TOTAL CHK"]
    ytd_data = result_dataframe.copy()
    ytd_data = ytd_data[(ytd_data["EMP ID"] == "10001")]
    ytd_data['MONTH YEAR'] = ytd_data[['MONTH', 'YEAR']].apply(
        lambda x: '_'.join(x), axis=1)
    ytd_data = ytd_data[ytd_data["MONTH YEAR"].isin(elligible_months)]
    ytd_data = ytd_data[["EMP ID"]+numerical_column]
    ytd_data = ytd_data.apply(
        pd.to_numeric, errors="coerce").fillna(0)
    ytd_data = ytd_data.groupby(["EMP ID"]).sum()
    ytd_data.reset_index(inplace=True)
    ytd_data = ytd_data.to_dict(orient="records")[0]
    result = {"YTD "+key: val for key, val in ytd_data.items()}
    result.update(current_month_data)
    return result


print(run())
