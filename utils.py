import csv
import time
timestamp = 0

def loadWebsites():
    with open('./resources/tranco_X5XLN.csv') as file:
        lines = file.readlines()
        return lines[20:]

def get(website):
    return website.split(",")[1]

def startTime():
    timestamp = time.time()

def stopTime():
    print("Time: "+str(time.time()-timestamp))
    print(time.time())