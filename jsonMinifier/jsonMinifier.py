#!/usr/bin/env python
"""Utility script that will minify a json file."""

import requests
import json

__author__ = "Javier Grande Pérez"
__version__ = "1.0.0"
__maintainer__ = "Javier Grande Pérez"
__email__ = "raven.berserk@gmail.com"
__status__ = "Production"


def read_json(json_path: str)->dict:
    """ Auxiliar method, that will read the json file from a URL. """

    response = requests.get(json_path)
    return response.json() if response.ok else response.raise_for_status()


def main():
    """ Main method, that will be responsible for minifier the json file. """

    # Fist, it is needed get the json file from the URL.
    json_file = read_json(input('Please indicate the json file URL: '))

    # Print the minify json file.
    print(json.dumps(json_file, separators=(',', ':')))
    print('Process completed successfully :)')


if __name__ == '__main__':
    main()
