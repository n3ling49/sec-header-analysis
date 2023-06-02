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
result = modes.multiScan(websites, 2)
stopTime2 = time.time()
#print("\nTime Single: "+str(stopTime1-startTime1))
print(str(result))
print("\nTime Multi: "+str(stopTime2-startTime2))
utils.save(result)
