import json
import time
import os

TIME = time.strftime("%Y-%m-%d_%H:%M:%S_", time.localtime())

def loadWebsites(website_amt):
    with open('/app/resources/top-1m.csv') as file:
        lines = file.readlines()
        return lines[len(lines)-website_amt:]
def get(website):
    return website.split(",")[1].replace("\n", "")

def save(dict, name = ""):
    name_final = name + TIME
    with open("/app/results/"+name_final+"results.json","w") as write_file:
        json.dump(dict, write_file, indent=4)

def save_multiple_files(dict, name = ""):
    name_final = name + TIME
    for key in dict.keys():
        with open("/app/results/"+name_final+"/"+key+".json","w") as write_file:
            json.dump(dict[key], write_file, indent=4)

def save_single_file(dict_entry, key, name = ""):
    name_final = name + TIME
    with open("/app/results/"+name_final+"/"+key+".json","w") as write_file:
        json.dump(dict_entry, write_file, indent=4)

def create_results_dir():
    os.mkdir("/app/results/"+TIME)