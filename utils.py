import json
import time

def loadWebsites():
    with open('./resources/tranco_X5XLN.csv') as file:
        lines = file.readlines()
        return lines[20:]
def get(website):
    return website.split(",")[1].replace("\n", "")

def save(dict):
    name = time.strftime("%Y-%m-%d_%H:%M:%S_", time.localtime())

    with open("./results/"+name+"results.json","w") as write_file:
        json.dump(dict, write_file, indent=4)