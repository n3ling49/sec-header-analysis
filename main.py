import json
import pathlib
import time
import utils
import modes

websites = utils.loadWebsites()
workingDir = pathlib.Path().resolve()

secHeaders = []
with open(str(workingDir)+'/resources/securityheaders.json') as jsonfile:
    secHeaders = json.load(jsonfile)['headers']

print(secHeaders)
#startTime1 = time.time()
#modes.scanWebsites(websites)
#stopTime1 = time.time()
startTime2 = time.time()
modes.multiScan(websites, 6)
stopTime2 = time.time()
#print("\nTime Single: "+str(stopTime1-startTime1))
print("\nTime Multi: "+str(stopTime2-startTime2))
