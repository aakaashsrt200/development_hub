from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from selenium import webdriver 

def OpenSite(driver, link):
	driver.get(link)
	return driver

chromeOptions = webdriver.ChromeOptions() 
#chromeOptions.add_argument("user-data-dir=/Users/CIPL-0036/Library/Application Support/Google/Chrome/Default/")
chromeOptions.add_experimental_option("detach", True)
#options.add_argument("download.default_directory=D:/MyPersonal/ProjectSankar/FileDownload/")
driver = webdriver.Chrome(executable_path='D:/MyPersonal/ProjectSankar/FileDownload/chromedriver.exe',chrome_options=chromeOptions)
driver = OpenSite(driver,'https://www.gst.gov.in/')