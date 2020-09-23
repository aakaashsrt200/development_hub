#==============================================================================
#title           :blob_upload.py
#description     :Automate the file uploads to Blob from local system
#author          :Aakaash Ramnath
#date            :23-Dec-2019
#version         :0.1
#usage           :Upload files from local MS Windows system storage to Azure Blob storage 
#notes           :
#python_version  :3.7.3
#==============================================================================

#==============================================================================
# External Libraries
#==============================================================================
from azure.storage.blob import BlockBlobService
import os
import sys
from colorama import init, Fore, Back, Style
import datetime
from datetime import datetime, timedelta
import configparser
import time
import pathlib
import shutil

CONST_PRINT_TRACE = ' : INFO : '
CONST_PRINT_GENERIC = ' : '
CONST_PRINT_EXIT = ' : EXIT : '
CONST_PRINT_ENTRY = ' : ENTRY : '
CONST_PRINT_WARNING = ' : WARNING : '
CONST_PRINT_ERROR = ' : ERROR : '

CONST_CONFIG_FILE = 'config.ini'

CONST_PROGRAM_SUCCESS_CODE = 0
CONST_PROGRAM_FAILURE_CODE = 1

CONST_CONFIG_KEY_LOCAL_INFO = 'LOCAL_INFO'
CONST_CONFIG_KEY_BLOB_INFO = 'BLOB_INFO'
CONST_CONFIG_LOCAL_PATH = 'local_path'
CONST_CONFIG_EXTENSION_LIST = 'extension_list'
CONST_CONFIG_ACTION_ON_FILE = 'action_on_file'
CONST_CONFIG_BLOB_NAME = 'blob_name'
CONST_CONFIG_BLOB_KEY = 'blob_key'
CONST_CONFIG_BLOB_CONTAINER = 'blob_container'
CONST_CONFIG_BLOB_PATH = 'blob_path'
CONST_CONFIG_DESTINATION_PATH = 'destination_path'

account_name=''
account_key=''
container=''

#Get values from config .INI file
def _get_config_value(path, key, value):
	# Connect to conf.ini and get the values
	appConfig = configparser.ConfigParser()
	config_path = path
	#print(config_path)
	appConfig.read(config_path)
	data = appConfig.get(key, value)
	return data

def _ensureDirectory(folder_path):
	try:
		pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
	except Exception as e:
		_print(CONST_PRINT_WARNING + "Couldn't create folder : " + folder_path)
		_print(CONST_PRINT_WARNING + str(e))

def _error_exit(m):
	_print(CONST_PRINT_ERROR + str(m))
	sys.exit(CONST_PROGRAM_FAILURE_CODE)

def _getTimestamp():
	return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def _print(message):
	init(convert=True)
	if 'ERROR' in message:
		print(Fore.RED +  _getTimestamp() + message )
	elif 'WARNING' in message: 
		print(Fore.YELLOW +  _getTimestamp() + message )
	elif 'INFO' in message: 
		print(Fore.GREEN +  _getTimestamp() + message )
	else:
		print(Fore.WHITE +  _getTimestamp() + message )

#List the number of files in the given folder
def fileList(path, extension):
	filelist = []
	for root,dirs,files in os.walk(path): 
		for filename in files:
			if filename.endswith(extension):
				filelist.append(filename)
	return filelist

def deleteFile(fpath):
	if os.path.exists(fpath):
		os.remove(fpath)
		return True
	else:
		print("The file does not exist or other issue while removing the file : " + fpath)
		return False

def moveFiles(src_path, dest_path, file):
	try:
		_ensureDirectory(dest_path)
		source_path = src_path + file
		destination_path = dest_path + '/' + file
		shutil.move(source_path, destination_path)
	except Exception as e:
		_print(CONST_PRINT_WARNING + "Some issue while moving the file to destination folder : " + dest_path)
		_print(CONST_PRINT_WARNING + str(e))

#Function to connect to blob
def connectToBlob(account, key):
	try:
		blob_service=BlockBlobService(account_name=account,account_key=key)
		return blob_service
	except Exception as e:
		_print(CONST_PRINT_ERROR + "Couldn't connect to blob storage")
		_print(CONST_PRINT_ERROR + str(e))
		sys.exit(0)

#Funstion to upload file to blob
def upload_to_blob(blob, container, local_folder_path, blob_folder_path, file_name):
	try:
		blob_path = blob_folder_path + file_name #Amazon/sample/ + sample_test.csv
		local_file_path = local_folder_path + file_name #C:/path/to/the/file/ + sample_test.csv
		blob.create_blob_from_path(container,blob_path,local_file_path)
		return True
	except Exception as e:
		_print(CONST_PRINT_WARNING + "Couldn't upload the file --> " + local_folder_path + file_name)
		_print(CONST_PRINT_WARNING + str(e))
		return False

def validate_config(configpath):
	try:
		ls_local_path = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_LOCAL_PATH)
		ls_extension = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_EXTENSION_LIST)
		ls_blob_path = _get_config_value(configpath, CONST_CONFIG_KEY_BLOB_INFO, CONST_CONFIG_BLOB_PATH)
		ls_dest_path = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_DESTINATION_PATH)
		action_on_file = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_ACTION_ON_FILE)
		
		if len(ls_local_path.split(';')) == len(ls_extension.split(';')) == len(ls_blob_path.split(';')) == len(ls_dest_path.split(';')):
			pass
		else:
			_error_exit("Config Validation Failed : Number of elements in local path list, blob path list, destination path list and extension list doesn't match. Please correct it and retry")

		if action_on_file.lower() == 'move':
			if ls_dest_path == '' or ls_dest_path == None or len(ls_dest_path) <= 3:
				_error_exit("Config Validation Failed : Unavailability of acceptable value in the destination path option (If you mentioned action as Move, then destination path should be provided)")

	except Exception as e:
		_error_exit(e)

#This function is generic to this use case and takes the whole responsibility from main function
def process(configpath):
	_print(CONST_PRINT_ENTRY + "process_upload")
	#Getting all the parameters from config file
	blob_key = _get_config_value(configpath, CONST_CONFIG_KEY_BLOB_INFO, CONST_CONFIG_BLOB_KEY)
	blob_name = _get_config_value(configpath, CONST_CONFIG_KEY_BLOB_INFO, CONST_CONFIG_BLOB_NAME)
	blob_container = _get_config_value(configpath, CONST_CONFIG_KEY_BLOB_INFO, CONST_CONFIG_BLOB_CONTAINER)
	blob_path = _get_config_value(configpath, CONST_CONFIG_KEY_BLOB_INFO, CONST_CONFIG_BLOB_PATH).split(';')
	local_path = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_LOCAL_PATH).split(';')
	extension_list = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_EXTENSION_LIST).split(';')
	action_on_file = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_ACTION_ON_FILE)
	destination_path = _get_config_value(configpath, CONST_CONFIG_KEY_LOCAL_INFO, CONST_CONFIG_DESTINATION_PATH).split(';')
	#Printing all the parameters from config file
	_print(CONST_PRINT_GENERIC + 'blob_key : ' + blob_key)
	_print(CONST_PRINT_GENERIC + 'blob_name : ' + blob_name)
	_print(CONST_PRINT_GENERIC + 'blob_container : ' + blob_container)
	_print(CONST_PRINT_GENERIC + 'action_on_file : ' + action_on_file)
	#Connect to blob and get the pointer to use it further
	try:
		blob = connectToBlob(blob_name, blob_key)
		_print(CONST_PRINT_TRACE + "Connection to Blob Storage : " + blob_name + ' --> Success')
	except Exception as e:
		_print(CONST_PRINT_ERROR + "Couldn't connect to blob --> " + blob_name)
		_error_exit(e)
	#Upload logic specific to this use case
	iter_count = len(local_path)
	#Iterating through different folders
	for i in range(0, iter_count):
		print('\n')
		_print(CONST_PRINT_TRACE + "Processing folder : " + local_path[i] + "\n")
		bpath = blob_path[i]
		lpath = local_path[i]
		ext = extension_list[i]
		_print(CONST_PRINT_GENERIC + 'Upload files to : ' + bpath)
		_print(CONST_PRINT_GENERIC + 'Upload files from : ' + lpath)
		_print(CONST_PRINT_GENERIC + 'Upload files of extension : ' + ext)
		files = fileList(lpath, ext)
		#print(files)
		#print(str(files))
		#Iterating through different files inside the current folder
		for file in files:
			upload_status = upload_to_blob(blob, blob_container, lpath, bpath, file)
			_print(CONST_PRINT_TRACE + "Upload file : " + container + '/' + bpath + file + ' --> Success')
			if action_on_file.lower() == 'copy':
				pass
			elif action_on_file.lower() == 'cut':
				if upload_status == True:
					delete_status = deleteFile(lpath + '/' + file)
					if delete_status == True:
						_print(CONST_PRINT_TRACE + "File Deleted: " + file)
				else:
					_print(CONST_PRINT_WARNING + 'Not deleting the file ' + file + ' since it is not uploaded/uploaded partially')
			elif action_on_file.lower() == 'move':
				if upload_status == True:
					dest_path = destination_path[i]
					moveFiles(lpath, dest_path, file)
					_print(CONST_PRINT_TRACE + "File moved to destination location : " + file)
				else:
					_print(CONST_PRINT_WARNING + 'Not moving the file ' + file + ' since it is not uploaded/uploaded partially')

	_print(CONST_PRINT_EXIT + "process")

def main():
	starttime = time.time()
	_print(CONST_PRINT_ENTRY + "main")
	validate_config(CONST_CONFIG_FILE)
	_print(CONST_PRINT_TRACE + CONST_CONFIG_FILE + " Validation Status --> Success")
	process(CONST_CONFIG_FILE)
	_print(CONST_PRINT_EXIT + "main")
	endtime = time.time()
	_print( CONST_PRINT_TRACE + "Time taken = %f seconds" %(endtime-starttime))

if __name__ == '__main__':
	_print("============ Execution Started ================")
	main()
	_print("============ All OK ================")
	sys.exit(CONST_PROGRAM_SUCCESS_CODE)
