import pysftp
import pathlib
import sys
from azure.storage.blob import BlockBlobService
import os

sftp_host = 'sftp.rbeu.rubikloud.com'
sftp_uname = 'rbsftp'
sftp_password = 'P*rK&lS#@1920'

blob_name = 'rbdevlrbuscacdevsa'
blob_key = '3gOpO3CzFb+/hsBBzHS+/fdDXfAFSkiEfpYmPcFWGkRVR5F0++Vg2N8Lnive7pLTUq5IiYhjViMC7h5QimCnwQ=='
blob_container = 'rawdata'
bpath = 'raw/RB/US/'
bdate = '/2019/11/19'
bpath_pos_daily = 'RB_POS_DAILY'
bpath_pos_weekly = 'RB_POS_WEEKLY'
bpath_material_master = 'RB_ITEM_MASTER'
bpath_soh = 'RB_SOH'
bpath_composed_product = 'COMPOSED_PRODUCT'
bpath_cust_wh_shto = ''
bpath_gic_uom = 'RB_GIC_UOM_CONVERSION'

local_path = r'D:\MyLearning\ReusableCodebases\SFTP-Blob\Temp'

def _ensureDirectory(folder_path):
	try:
		pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
	except:
		pass

def _silentfileremove(filename):
	try:
		os.remove(filename)
	except Exception as e: 
		pass

def connectToBlob(account, key):
	try:
		blob_service=BlockBlobService(account_name=account,account_key=key)
		return blob_service
	except Exception as e:
		print("Couldn't connect to blob storage")
		print('Error : ' + str(e))
		sys.exit(0)

#Funstion to upload file to blob
def upload_to_blob(blob, container, local_folder_path, blob_folder_path, file_name):
	try:
		blob_path = blob_folder_path + '\\' + file_name #Amazon/sample/ + sample_test.csv
		local_file_path = local_folder_path + '\\' + file_name #C:/path/to/the/file/ + sample_test.csv
		blob.create_blob_from_path(container,blob_path,local_file_path)
		return True
	except Exception as e:
		_print(CONST_PRINT_WARNING + "Couldn't upload the file --> " + local_folder_path + file_name)
		_print(CONST_PRINT_WARNING + str(e))
		return False

def download_upload(sftp, blob, file, bpath_dyn):
	print('======== : ' + file + ' : ========')
	print('--> downloading from SFTP ...')
	fpath = local_path + "\\" + file
	sftp.get(file, fpath)
	print('--> Download success')
	print('--> uploading to blob ...')
	blob_path = bpath + bpath_dyn + bdate
	status = upload_to_blob(blob, blob_container, local_path, blob_path, file)
	if status == True:
		print('--> Upload success \n')
		_silentfileremove(fpath)

blob = connectToBlob(blob_name, blob_key)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
# Make connection to sFTP
print("Connecting to SFTP ...")
with pysftp.Connection(sftp_host, username=sftp_uname, password=sftp_password, cnopts = cnopts) as sftp:
	print("Connection to SFTP : Success")
	with sftp.cd('files'):
		files = sftp.listdir()
		if files != None:
			_ensureDirectory(local_path)
		for file in files:
			blob = connectToBlob(blob_name, blob_key)
			if 'MATERIAL_MASTER' in file.upper():
				download_upload(sftp, blob, file, bpath_material_master)
			if 'POS_DAILY' in file.upper():
				download_upload(sftp, blob, file, bpath_pos_daily)
			if 'POS_WEEKLY' in file.upper():
				download_upload(sftp, blob, file, bpath_pos_weekly)
			if 'SOH_HISTORICAL' in file.upper():
				download_upload(sftp, blob, file, bpath_soh)
			if 'COMPOSED_PRODUCT' in file.upper():
				download_upload(sftp, blob, file, bpath_soh)
sftp.close()