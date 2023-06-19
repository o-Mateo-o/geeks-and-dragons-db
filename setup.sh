#!/bin/sh
pip install virtualenv 				                                # install the virtual environment manager
# Python path - can be altered down there !!!!!
"~/AppData/Local/Programs/Python/Python39/python.exe" -m venv .venv	# create a virtual environment 
source .venv/Scripts/activate                                       # activate the virtual environment
pip install --upgrade pip						                    # upgrade pip
pip install -r requirements.txt			                	        # install dependencies
