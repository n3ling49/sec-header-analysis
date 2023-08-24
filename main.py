import json
import pathlib
import time
import utils
import modes
import script

WEBSITEAMT = 250

websites = utils.loadWebsites(WEBSITEAMT)
workingDir = pathlib.Path().resolve()

#startTime1 = time.time()
#modes.scanWebsites(websites)
#stopTime1 = time.time()
startTime2 = time.time()
result = modes.multiScan(websites, 14)
stopTime2 = time.time()
#print("\nTime Single: "+str(stopTime1-startTime1))
print("\nTime Multi: "+str(stopTime2-startTime2))
script.getfailed(result)
utils.save(result)
