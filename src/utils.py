import json
import time
import os
import math
import shutil
import stat
from config import RESULT_FOLDER

TIME = time.strftime("%Y-%m-%d_%H:%M:%S_", time.localtime())

def loadWebsites(end, start = 0):
    with open('/app/resources/top-1m.csv') as file:
        lines = file.readlines()
        return lines[start:end]
def get(website):
    return website.split(",")[1].replace("\n", "")

def save(dict, name = ""):
    name_final = None
    if RESULT_FOLDER == "":
        name_final = name + TIME
    else: 
        name_final = name + RESULT_FOLDER

    with open("/app/results/"+name_final+"results.json","w") as write_file:
        json.dump(dict, write_file, indent=4)

def save_multiple_files(dict, name = ""):
    name_final = None
    if RESULT_FOLDER == "":
        name_final = name + TIME
    else: 
        name_final = name + RESULT_FOLDER

    for key in dict.keys():
        with open("/app/results/"+name_final+"/"+key+".json","w") as write_file:
            json.dump(dict[key], write_file, indent=4)

def save_single_file(dict_entry, key, name = "", website_nr = ""):

    result_folder_name = None
    if RESULT_FOLDER == "":
        result_folder_name = name + TIME
    else: result_folder_name = name + RESULT_FOLDER

    if website_nr != "":
        big_start_range = str(int(round_down(int(website_nr) - 1, -5) + 1))
        big_end_range = str(int(big_start_range) + 100000)
        start_range = str(int(round_down(int(website_nr) - 1, -3) + 1))
        end_range = str(int(start_range) + 999)
        json_folder_name = big_start_range+"-"+big_end_range+"/"+start_range + "-" + end_range
        if not os.path.exists("/app/results/"+result_folder_name+"/"+big_start_range+"-"+big_end_range):
            os.mkdir("/app/results/"+result_folder_name+"/"+big_start_range+"-"+big_end_range)
        if not os.path.exists("/app/results/"+result_folder_name+"/"+json_folder_name):
            os.mkdir("/app/results/"+result_folder_name+"/"+json_folder_name)
        result_folder_name = result_folder_name + "/" + json_folder_name

    with open("/app/results/"+result_folder_name+"/"+key+".json","w") as write_file:
        json.dump(dict_entry, write_file, indent=4)

def create_results_dir():
    os.mkdir("/app/results/"+TIME)

def round_up(n, decimals=0):
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier

def round_down(n, decimals=0):
    multiplier = 10**decimals
    return math.floor(n * multiplier) / multiplier

def divide_chunks(list, chunk_size): 
      
    for i in range(0, len(list), chunk_size):  
        yield list[i:i + chunk_size] 

def init_process_dir(pid):
    os.mkdir("/app/processdata/PROFILE"+str(pid))
    #os.mkdir("/root/.local/PROFILE"+str(pid))
    shutil.copyfile("/usr/bin/chromedriver", "/app/processdata/PROFILE"+str(pid)+"/chromedriver")
    os.chmod("/app/processdata/PROFILE"+str(pid)+"/chromedriver", os.stat("/usr/bin/chromedriver").st_mode | stat.S_IXUSR)