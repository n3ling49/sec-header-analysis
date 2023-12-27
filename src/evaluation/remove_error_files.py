import os
import json

results_folder = "ba_dataset/"
this_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(this_dir, '../../results/'+results_folder)

subdirs = os.listdir(results_dir)
errors = dict()
errors["total"] = 0
errors["last"] = 0
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
                data = None
                delete = False
                counter = 0
                with open(os.path.join(results_dir, dir, subdir, file)) as json_file:
                    try:
                        data = list(json.loads(json_file.read()))
                    except:
                        print("Error reading file: "+os.path.join(results_dir, dir, subdir, file))
                        continue
                    for entry in data:
                        counter += 1
                        if "error" in entry:
                            delete = True
                            break
                if delete:
                    errors["total"] += 1
                    os.remove(os.path.join(results_dir, dir, subdir, file))
                if delete and len(data) == counter:
                    errors["last"] += 1
print(f'Total errors: {errors["total"]}')
print(f'Errors in last request: {errors["last"]}')