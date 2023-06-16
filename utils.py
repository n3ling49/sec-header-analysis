import json

def loadWebsites():
    with open('./resources/tranco_X5XLN.csv') as file:
        lines = file.readlines()
        return lines[20:]
def get(website):
    return website.split(",")[1].replace("\n", "")

def save(dict):
    with open("./results/results.json","w") as write_file:
        json.dump(dict, write_file, indent=4)