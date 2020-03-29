This code base can upload any number of files from local windows system to any Azure Blob storage locations. The file uploads are configuratioin driven (config.ini).

Must to have : 
	1. blob_upload.py file
	2. config.ini file
	3. Python 3.7.x

Libraries to be installed :
	1. azure.storage.blob
	2. colorama
	3. datetime
	4. time
	5. configparser

How to configure the config.ini file?
	local_path :
		-> This says files should be picked from which path
		-> Always use (/) and do not use (\)
		-> Always end the folder path with slash (/)
		-> Do not miss out the slash at the end (/)
		-> Do not provide the file names in the path
		-> Can provide multiple paths separated by semi colon (;)
	extension_list :
		-> This says what extension files should be uploaded to blob from the given folder location
		-> Provide the full extension with dot (.csv) or (.xlsx)
		-> Multiple extensions can be provided separated by semi colon (;)
		-> Make sure number of extension provided should be equal to number of folder paths provided in local_path parameter
	action_on_file :
		-> This specifies whether the file should be copied or moved
		-> 3 options are supported
		-> copy or move or delete
	destination_path
		--> This says files should be moved to which path
		--> Always use (/) and do not use (\)
		--> Always end the folder path with slash (/)
		--> Do not add slashes at the end (/)
		--> Do not provide the file names in the path
		--> Can provide multiple paths separated by semi colon (;)

	blob_name :
		-> Used to connect to the specific blob where the files had to be uploaded
	blob_key :
		-> Used to connect to the specific blob where the files has to be uploaded
		-> The configuration files are not encrypted. Please keep the config file safely
	blob_container :
		-> This specifies in which container the files has to be uploaded
	blob_path :
		-> This says files should be uploaded to which paths
		-> Always use (/) and do not use (\)
		-> Always end the folder paths with slash (/)
		-> Do not miss out the slash at the end (/)
		-> Do not provide the file names in the paths
		-> Do not provide the container name in the paths
		-> Can provide multiple paths separated by semi colon (;)
		-> Make sure number of extension provided should be equal to number of folder paths provided in local_path parameter
		
	local_path --> extension_list --> destination_path --> blob_path are assumed to have one-to-one relationship. Make sure you provide equal number of entities (Seperated by semicolon ;) in all the 4 options
	
Output inference :
	* All the status information are provided in Green colour (Which means success)
	* All the debugging information are printed in White colout
	* All the warning messages are printed in Yellow colour
	* All error messages are printed in Red colour
	* Make sure you see "All OK" message at the end of the execution to conclude that the code has ended successfully
	
Integration related information : 
	> Program success code = 0
	> Program failure code = 1