"""
Author: Javier Grande Pérez
Description: Utility script that will minify a json file.
"""

import requests
import json

def read_json(jsonPath:str)->dict:
    """ Auxiliar method, that will read the json file from a URL. """
    
    response = requests.get(jsonPath)
    return response.json() if response.ok else response.raise_for_status()

def json_minifier():
    """ Main method, that will be responsible for minifier the json file. """

    # Fist, it is needed get the json file from the URL.
    jsonFile = read_json(input('Please indicate the json file URL: '))

    # Print the minify json file.
    print(json.dumps(jsonFile,separators=(',',':')))
    print('Process completed successfully :)')
