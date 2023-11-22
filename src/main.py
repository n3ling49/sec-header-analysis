import pathlib
import time
import utils as utils
import modes as modes
import script as script
import requests
from zipfile import ZipFile
import clear_results as clear_results

WEBSITEAMT = 100
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"
CLEAR = True
CLEAR_EXCEPTIONS = []

if __name__ == '__main__':
    # Clearing the results folder
    if CLEAR:
        print("Clearing results folder")
        clear_results.clear('../results/',CLEAR_EXCEPTIONS)
        print("Clearing processdata folder")
        clear_results.clear('../processdata/')
    # Pulling the latest top 1 million websites list from Tranco
    r = requests.get(TRANCO_URL, allow_redirects=True)
    open('top-1m.csv.zip', 'wb').write(r.content)
    with ZipFile('top-1m.csv.zip', 'r') as zipObj:
        zipObj.extractall(path='/app/resources/')
    # Loading a subset of websites from the list

    websites = utils.loadWebsites(WEBSITEAMT)
    workingDir = pathlib.Path().resolve()
    utils.create_results_dir()

    #fetching the websites
    startTime2 = time.time()
    result = modes.multiScan(websites, 10)
    stopTime2 = time.time()
    print("\nTime Multi: "+str(stopTime2-startTime2))
    script.getfailed(result)