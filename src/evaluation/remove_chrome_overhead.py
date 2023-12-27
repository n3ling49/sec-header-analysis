import os
import json

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
                data = None
                with open(os.path.join(results_dir, dir, subdir, file)) as json_file:
                    try:
                        data = list(json.loads(json_file.read()))
                    except:
                        print("Error reading file: "+os.path.join(results_dir, dir, subdir, file))
                        continue
                    counter = 0
                    start_index = 0
                    https_found = False
                    http_found = False
                    for entry in data:
                        if not "request" in entry:
                            continue
                        request = entry["request"]
                        if type(request) == str:
                            request = json.loads(request)
                        url = request["url"]
                        is_http = url == f'http://{website_name}/'
                        if (not https_found and url == f'https://{website_name}/') or (not http_found and is_http):
                            start_index = counter
                            if is_http:
                                http_found = True
                                break
                            else:
                                https_found = True
                        counter += 1
                    if not https_found and not http_found:
                        start_index = counter
                    data = data[start_index:]
                if len(data) == 0:
                        os.remove(os.path.join(results_dir, dir, subdir, file))
                        continue
                with open(os.path.join(results_dir, dir, subdir, file), "w") as json_file:
                    json.dump(data, json_file)
