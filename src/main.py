import pathlib
import os
import time
import utils as utils
import modes as modes
import script as script
import requests
from zipfile import ZipFile
import clear_results as clear_results
from config import CLEAR_RESULTS, CLEAR_RESULTS_EXCEPTIONS, CLEAR_PROCESSDATA, DOWNLOAD_TRANCO, PROCESS_AMT, WEBSITE_START, WEBSITE_END, WEBSITES_PER_THREAD, RESULT_FOLDER
import logging
import threading
import psutil
import pgrep
import signal

TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s', handlers=[
    logging.FileHandler('/app/results/secheader.log'),
    logging.StreamHandler()
    ])

    selenium_logger = logging.getLogger('seleniumwire')
    selenium_logger.setLevel(logging.ERROR)
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
    if RESULT_FOLDER == "":
        utils.create_results_dir()
    websites = utils.loadWebsites(WEBSITE_END, WEBSITE_START)
    chunk_size = WEBSITES_PER_THREAD * PROCESS_AMT
    website_chunks = list(utils.divide_chunks(websites, chunk_size))
    workingDir = pathlib.Path().resolve()

    #fetching the websites
    startTime2 = time.time()

    result = dict()
    for i in range(0, len(website_chunks)):
        logging.info('New Website Chunk')
        logging.info(f'Main Process running Threads: {threading.active_count()}')
        logging.info(f'Main Process RAM memory % used:', psutil.virtual_memory()[2])
        logging.info('===========================')
        processes = pgrep.pgrep('chrome')
        logging.info(f'Chrome processes running: {len(processes)}')
        logging.info('===========================')
        #init_dir = i == 0
        logging.info('Clearing active chrome processes...')
        for p in processes:
            os.kill(p, signal.SIGKILL)
        logging.info('===========================')
        processes = pgrep.pgrep('chrome')
        logging.info(f'Chrome processes running: {len(processes)}')
        logging.info('===========================')
        result.update(modes.multiScan(website_chunks[i], PROCESS_AMT, True))
        logging.info('Clearing processdata folder')
        clear_results.clear('../processdata/')
    
    stopTime2 = time.time()
    print("\nTime Multi: "+str(stopTime2-startTime2))
    script.getfailed(result)