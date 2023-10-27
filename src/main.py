import pathlib
import time
import utils as utils
import modes as modes
import script as script
import requests
from zipfile import ZipFile
import os

WEBSITEAMT = 100
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

# Pulling the latest top 1 million websites list from Tranco

r = requests.get(TRANCO_URL, allow_redirects=True)
open('top-1m.csv.zip', 'wb').write(r.content)
with ZipFile('top-1m.csv.zip', 'r') as zipObj:
    zipObj.extractall(path='/app/resources/')
print(os.listdir('/app/resources'))
# Loading a subset of websites from the list

websites = utils.loadWebsites(WEBSITEAMT)
workingDir = pathlib.Path().resolve()
utils.create_results_dir()

#fetching the websites

#startTime1 = time.time()
#modes.scanWebsites(websites)
#stopTime1 = time.time()
startTime2 = time.time()
result = modes.multiScan(websites, 14)
stopTime2 = time.time()
#print("\nTime Single: "+str(stopTime1-startTime1))
print("\nTime Multi: "+str(stopTime2-startTime2))
script.getfailed(result)
#utils.save_multiple_files(result)
