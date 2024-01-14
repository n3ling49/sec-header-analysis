import os
import json
import eval_utils
import math

CHUNK_SIZE = 4

def overhead():
    results_dir = "../../results/ba_dataset/"
    subdirs = os.listdir(results_dir)

    counter = 0
    acc_body_size = []
    valid_sites = []
    total_responses = []

    chunk_acc_body_size = 0
    chunk_total_responses = 0
    chunk_valid_sites = 0

    min_body_size = math.inf
    max_body_size = 0
    min_website_size = math.inf
    max_website_size = 0

    subdirs.sort(key=eval_utils.sortfunc)
    for dir in subdirs:
        sub_subdirs = os.listdir(os.path.join(results_dir, dir))
        #print(sub_subdirs)
        print(dir)
        sub_subdirs.sort(key=eval_utils.sortfunc)
        for subdir in sub_subdirs:
            counter += 1
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
                        if not is_valid_object(data, website_name):
                            continue
                        chunk_valid_sites += 1
                        website_body = 0
                        for entry in data:
                            if not "request" in entry:
                                continue
                            if type(entry["request"]) == str:
                                entry["request"] = json.loads(entry["request"])
                            if not "response" in entry:
                                continue
                            response = entry["response"]
                            if type(response) == str:
                                response = json.loads(response)
                            headers = response["headers"]
                            if type(headers) == str:
                                headers = json.loads(headers)
                            for header in headers:
                                if header.lower() == "content-length":
                                    chunk_acc_body_size += int(headers[header])
                                    if int(headers[header]) < min_body_size:
                                        min_body_size = int(headers[header])
                                    if int(headers[header]) > max_body_size:
                                        max_body_size = int(headers[header])
                                    website_body += int(headers[header])
                                    break
                            chunk_total_responses += 1
                        if website_body < min_website_size:
                            min_website_size = website_body
                        if website_body > max_website_size:
                            max_website_size = website_body
            if counter == CHUNK_SIZE:
                acc_body_size.append(chunk_acc_body_size)
                total_responses.append(chunk_total_responses)
                valid_sites.append(chunk_valid_sites)
                counter = 0
                chunk_acc_body_size = 0
                chunk_total_responses = 0
                chunk_valid_sites = 0
    print(acc_body_size)
    print(total_responses)
    print(valid_sites)
    print(min_body_size)
    print(max_body_size)
    print(min_website_size)
    print(max_website_size)
    



def is_valid_object(req_res_err_arr, website_name):
    response = None
    for entry in req_res_err_arr:
        if type(entry) == str:
            entry = json.loads(entry)
        request = entry["request"]
        if type(request) == str:
            request = json.loads(request)
        if eval_utils.is_initial_request(request, website_name):
            response = eval_utils.find_initial_response(entry, req_res_err_arr, website_name)
            break
    if response is None:
        return False
    if type(response) == str:
        response = json.loads(response)
    if bot_detected(response):
        return False
    return True


def bot_detected(res):
    if not type(res["status_code"]) == str:
        res["status_code"] = str(res["status_code"])
    if res["status_code"][0] == "4":
        return True
    return False

def calculate_header_size(header, value):
    return len(header) + len(value) + 3

overhead()