import sys
import os.path
import pandas as pd
import xlrd
import xlwt
import glob
from datetime import datetime
from datetime import datetime, timedelta
import shutil
import configparser
from zipfile import ZipFile
import openpyxl
import selenium
from html.parser import HTMLParser
import csv
import webbrowser
from bs4 import BeautifulSoup
import bs4 as bs
from selenium import webdriver 
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
#import selenium.webdriver.common.keys.Keys as Keys
from selenium.webdriver.common.keys import Keys

#==============================================================================
# Constants used through out the code
#==============================================================================
PROGRAM_FAILURE = 2
PROGRAM_SUCCESS = 1

CONST_METHOD_ENTRY = ' : Entry : '
CONST_METHOD_EXIT  = ' : Exit  : '
CONST_PRINT_STEP   = ' : Step  : '
CONST_PRINT_TRACE  = ' : Info  : '
CONST_PRINT_ERROR  = ' : ERROR : '
CONST_PRINT_WARNING  = ' : WARNING : '
CONST_METHOD_TEST = ' : TEST : ******** : '

CONST_CONFIG_FILENAME = 'Config.ini'

CONST_LOG_FOLDER_NAME = "Logs"
CONST_FILE_EXTENSION_EXCEL = ".xlsx"
CONST_FILE_EXTENSION_ZIP = ".zip"

CONFIG_SECTION_OPTIONS = 'options'

CONFIG_KEY_HYPERLINK = 'hyperlink'
CONFIG_KEY_USERNAME = 'username'
CONFIG_KEY_PASSWORD = 'password'
CONFIG_KEY_PERIOD = 'period'
CONFIG_KEY_MONTHS = 'months'
CONFIG_KEY_RUN_DOWNLOAD = 'run_download'

#==============================================================================
# Utility functions
#==============================================================================
def _getTimestamp():
	return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def _getTimestampasnum():
	return str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
#To print the message
def _print(message):
	print( _getTimestamp() + message)
# Read config file and get value by the key
def _get_config_value(path, key, value):
	# Connect to conf.ini and get the values
	appConfig = configparser.ConfigParser()
	#config_path = path + "\\" + CONST_CONFIG_PARSER_FOLDER
	#print(config_path)
	appConfig.read(path)
	data = appConfig.get(key, value)
	return data
# To create a folder path if not exist
def _ensureDirectory(folder_path):
	try:
		pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True) 
	except:
		pass

def _errorExit(errorDescription):
	if (_isBlank(errorDescription) == False):
		_print( CONST_PRINT_ERROR + ' ***** ERROR : ' + errorDescription)
	else:
		_print(CONST_PRINT_ERROR + ' ***** ERROR : Terminating with some error')
	sys.exit(PROGRAM_FAILURE) #termination with error
	raise
# Returns true is the string is blank
def _isBlank (myString):
	if myString is None:
		return True
	else:
		myString = str(myString)
	if myString and myString.strip():
		#myString is not None AND myString is not empty or blank
		return False
	#myString is None OR myString is empty or blank
	return True
# Return true if the path exists
def _checkPath(path):
	return os.path.exists(path)
# To delete a file from a path
def _silentfileremove(filename):
	print(filename)
	try:
		filename = filename.replace("\\","\\\\")
		#_print(filename)
		os.remove(str(filename))
	except Exception as e: 
		#_print(str(e))
		pass
# Returns the liast of Excel files present in the location
def _GetExcelFileList(path):
	filelist = []
	for root,dirs,files in os.walk(path): 
		for filename in files:
			if filename.endswith('xlsx'):
				filelist.append(filename)
		break
	return filelist

def _GetFileList(path, endswith):
	filelist = []
	for root,dirs,files in os.walk(path): 
		for filename in files:
			if filename.endswith(endswith):
				filelist.append(filename)
		break
	return filelist

#==============================================================================
# Processing functions
#==============================================================================
hyperlink = _get_config_value(CONST_CONFIG_FILENAME, CONFIG_SECTION_OPTIONS,CONFIG_KEY_HYPERLINK)
username = _get_config_value(CONST_CONFIG_FILENAME, CONFIG_SECTION_OPTIONS,CONFIG_KEY_USERNAME)
password = _get_config_value(CONST_CONFIG_FILENAME, CONFIG_SECTION_OPTIONS,CONFIG_KEY_PASSWORD)
period = _get_config_value(CONST_CONFIG_FILENAME, CONFIG_SECTION_OPTIONS,CONFIG_KEY_PERIOD)
months = _get_config_value(CONST_CONFIG_FILENAME, CONFIG_SECTION_OPTIONS,CONFIG_KEY_MONTHS)
run_download = _get_config_value(CONST_CONFIG_FILENAME, CONFIG_SECTION_OPTIONS,CONFIG_KEY_RUN_DOWNLOAD)

if _isBlank(hyperlink) == True:
	hyperlink='https://www.gst.gov.in/'
if _isBlank(username) == True:
	_errorExit("Provide username in Config.ini file")
if _isBlank(password) == True:
	_errorExit("Provide password in Config.ini file")
if _isBlank(password) == True:
	_print(CONST_PRINT_WARNING + "Default : Period 2018-19 is chosen since Config.ini file was left blank for that option")
	period='2018-19'
if months.lower() == 'all' or _isBlank(months) == True:
	_print(CONST_PRINT_WARNING + "Default : All months are chosen since Config.ini file was left blank for that option")
	months=['April','May','June','July','August','September','October','November','December','January','February','March']
else:
	try:
		months=months.split(';')
	except:
		months=['April','May','June','July','August','September','October','November','December','January','February','March']
if _isBlank(password) == True:
	_print(CONST_PRINT_WARNING + "Default : Download is set to false since Config.ini file was left blank for that option")
	run_download='true'

def sleep(sec):
	time.sleep(sec)

def OpenSite(driver, link):
	driver.get(link)
	return driver

def FindXpathElement(driver, xpath):
	try:
		click_element = driver.find_element_by_xpath(xpath)
		return click_element
	except:
		sleep(10)
		click_element = driver.find_element_by_xpath(xpath)
		return click_element

def FindCSSElemet(driver, selector):
	try:
		click_element = driver.find_element_by_css_selector(selector)
		return click_element
	except:
		sleep(10)
		click_element = driver.find_element_by_css_selector(selector)
		return click_elemen
		
def operationDownload(driver):
	click_download = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[7]/span/a')
	click_download.click()

def operationLogout(driver):
	logout = FindXpathElement(driver, '/html/body/div[1]/ng-include[1]/header/div[2]/div/div/ul/li/div/a')
	logout.click()
	logout = FindXpathElement(driver, '/html/body/div[1]/ng-include[1]/header/div[2]/div/div/ul/li/div/ul/li[5]/a')
	logout.click()
	sleep(5)

def operationForcedLogout(driver):
	logout = FindXpathElement(driver, '/html/body/div[1]/header/div[2]/div/div/ul/li/div/a/span')
	logout.click()
	logout = FindXpathElement(driver, '/html/body/div[1]/header/div[2]/div/div/ul/li/div/ul/li[5]/a')
	logout.click()
	sleep(5)

def operationLogin(driver):
	login = FindXpathElement(driver, '/html/body/div[1]/header/div[2]/div/div/ul/li/a')
	login.click()
	sleep(3)
	uname = FindXpathElement(driver, '//*[@id="username"]')
	uname.send_keys(username)
	pword = FindXpathElement(driver, '//*[@id="user_pass"]')
	pword.send_keys(password)
	sleep(10)
	submit = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/div/form/div[6]/div/button')
	submit.click()
	sleep(5)
	_print(CONST_PRINT_TRACE + "Hurray!!!! Logged in")

def WebCrawl():
	chromeOptions = webdriver.ChromeOptions() 
	#chromeOptions.add_argument("user-data-dir=/Users/CIPL-0036/Library/Application Support/Google/Chrome/Default/")
	chromeOptions.add_experimental_option("detach", True)
	#options.add_argument("download.default_directory=D:/MyPersonal/ProjectSankar/FileDownload/")
	driver = webdriver.Chrome(executable_path='D:/MyPersonal/ProjectSankar/FileDownload/chromedriver.exe',chrome_options=chromeOptions)
	driver = OpenSite(driver,hyperlink)
	try:
		operationLogin(driver)
	except Exception as e:
		_print(CONST_PRINT_WARNING + 'Already logged into the site. If that is not the account you wanna login, please kill the process, logout, re-run')
		operationForcedLogout(driver)
		driver = OpenSite(driver,hyperlink)
		operationLogin(driver)
		pass
	return_dashboard = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/button/span')
	return_dashboard.click()
	sleep(5)
	_print(CONST_PRINT_TRACE + 'Entered into return dashboard')
	for month in months:
		select_year = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div/div[1]/select')
		select_year.click()
		select_year.send_keys(period)
		select_month = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div/div[2]/select')
		select_month.click()
		select_month.send_keys(month)
		_print(CONST_PRINT_TRACE + 'Chose year and months')
		search = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div/div[3]/button')
		#'body > div.content-wrapper.fade-ng-cloak > div.container > div > div:nth-child(2) > div.content-pane-returns > form > div > div:nth-child(3) > button'
		search.click()
		_print(CONST_PRINT_TRACE + 'Hit seacrh button too...')
		sleep(5)
		auto_drafted_details = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[3]/div[3]/div[1]/div[2]/div/div[2]/div/div[2]/button')
		auto_drafted_details.click()
		sleep(5)
		generate_download = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[6]/div/button')
		generate_download.click()
		_print(CONST_PRINT_TRACE + 'Made it to generate for the month : ' + month)
		sleep(5)
		if run_download.lower() == 'true':
			operationDownload(driver)
			sleep(5)
		back = FindXpathElement(driver, '/html/body/div[2]/div[2]/div/div[2]/div[1]/div[2]/div[9]/div/button')
		back.click()
		sleep(5)
	operationLogout(driver)
	sleep(15)
	

def main():
	_print(CONST_PRINT_TRACE + CONST_METHOD_ENTRY + "Program main\n")
	_print(CONST_PRINT_TRACE + 'hyperlink    : ' + hyperlink)
	_print(CONST_PRINT_TRACE + 'username     : ' + username)
	_print(CONST_PRINT_TRACE + 'password     : ' + password)
	_print(CONST_PRINT_TRACE + 'period       : ' + period)
	_print(CONST_PRINT_TRACE + 'months       : ' + str(months))
	_print(CONST_PRINT_TRACE + 'run_download : ' + run_download)
	WebCrawl()
	_print(CONST_PRINT_TRACE + CONST_METHOD_EXIT + "Program main")

if __name__ == '__main__':
	print("\n==================== Execution Started ==================\n")
	main()
	print("\n==================== All ok ==================\n")
	#sys.exit(PROGRAM_SUCCESS)