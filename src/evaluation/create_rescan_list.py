import os
import json

websites = []
with open('../../resources/top-1m.csv') as file:
    lines = file.readlines()
    websites = lines

in_dataset = dict()

for website in websites:
    domain = website.split(",")[1].replace("\n", "")
    in_dataset[domain] = dict()
    in_dataset[domain]["status"] = False
    in_dataset[domain]["string"] = website

results_folder = "ba_dataset/"
this_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(this_dir, '../../results/'+results_folder)

subdirs = os.listdir(results_dir)

for dir in subdirs:
    sub_subdirs = os.listdir(os.path.join(results_dir, dir))
    #print(sub_subdirs)
    print(dir)
    for subdir in sub_subdirs:
        files = os.listdir(os.path.join(results_dir, dir, subdir))
        #print(files)
        #print(subdir)
        for file in files:
            if file.endswith(".json"):
                website_name = file.split(".json")[0]
                in_dataset[website_name]["status"] = True

writelines = []
for website in in_dataset.keys():
    if not in_dataset[website]["status"]:
        writelines.append(in_dataset[website]["string"])

if os.path.exists("../../resources/rescan.csv"):
    os.remove("../../resources/rescan.csv")

with open("../../resources/rescan.csv", "w") as file:
    file.writelines(writelines)
