import pathlib
import os
import time
import utils as utils
import modes as modes
import script as script
import requests
from zipfile import ZipFile
import clear_results as clear_results
from config import CLEAR_RESULTS, CLEAR_RESULTS_EXCEPTIONS, CLEAR_PROCESSDATA, DOWNLOAD_TRANCO, PROCESS_AMT, WEBSITE_START, WEBSITE_END, WEBSITES_PER_THREAD

TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

if __name__ == '__main__':
    # Clearing the results folder
    if CLEAR_RESULTS:
        print("Clearing results folder")
        clear_results.clear('../results/',CLEAR_RESULTS_EXCEPTIONS)
    if CLEAR_PROCESSDATA:
        print("Clearing processdata folder")
        clear_results.clear('../processdata/')
    if DOWNLOAD_TRANCO:
        if pathlib.Path("/app/resources/top-1m.csv").exists():
           os.remove("/app/resources/top-1m.csv") 
        # Pulling the latest top 1 million websites list from Tranco
        r = requests.get(TRANCO_URL, allow_redirects=True)
        open('top-1m.csv.zip', 'wb').write(r.content)
        with ZipFile('top-1m.csv.zip', 'r') as zipObj:
            zipObj.extractall(path='/app/resources/')
        # Loading a subset of websites from the list

    websites = utils.loadWebsites(WEBSITE_END, WEBSITE_START)
    chunk_size = WEBSITES_PER_THREAD * PROCESS_AMT
    website_chunks = list(utils.divide_chunks(websites, chunk_size))
    workingDir = pathlib.Path().resolve()
    utils.create_results_dir()

    #fetching the websites
    startTime2 = time.time()

    result = dict()
    for i in range(0, len(website_chunks)):
        init_dir = i == 0
        result.update(modes.multiScan(website_chunks[i], PROCESS_AMT, init_dir))
    
    stopTime2 = time.time()
    print("\nTime Multi: "+str(stopTime2-startTime2))
    script.getfailed(result)