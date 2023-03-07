SHELL=powershell

ZIP_NAME="Axolotl.zip"

all: clear
	
run:
	.\run.bat

clear:
	rm -r test
	mkdir test
	if ( test-path ${ZIP_NAME} ) {rm ${ZIP_NAME}}

zip: clear
	7z a ${ZIP_NAME} '-xr!*/__pycache__' -- axolotl axolotl_gui instruments config main.py readme.md requirements.txt run.bat LICENSE
