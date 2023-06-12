#!/bin/sh
pip install virtualenv 				# install the virtual environment manager
working=$(dirname "$0")				# find the working dir
cd $working					# change the working dir
C:/Python310/python.exe -m venv .venv		# create a virtual environment (Python path can be altered)
source .venv/Scripts/activate			# activate the virtual environment
pip install -r requirements.txt			# install dependencies