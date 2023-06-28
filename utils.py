import json
import time

def loadWebsites(website_amt):
    with open('./resources/tranco_X5XLN.csv') as file:
        lines = file.readlines()
        return lines[:website_amt]
def get(website):
    return website.split(",")[1].replace("\n", "")

def save(dict):
    name = time.strftime("%Y-%m-%d_%H:%M:%S_", time.localtime())

    with open("./results/"+name+"results.json","w") as write_file:
        json.dump(dict, write_file, indent=4)