import os
import json
import eval_utils
import math

CHUNK_SIZE = 4

def overhead():
    results_dir = "../../results/ba_dataset/"
    this_dir = os.path.dirname(os.path.abspath(__file__))

    security_headers = []
    headers_dir = os.path.join(this_dir, '../../resources/securityheaders.json')
    with open(headers_dir) as file:
        security_headers = json.loads(file.read())["headers"]

    subdirs = os.listdir(results_dir)

    counter = 0
    acc_header_size = []
    valid_sites = []
    total_responses = []
    header_amount = []
    acc_secheader_size = []
    secheader_amount = []

    chunk_acc_header_size = 0
    chunk_total_responses = 0
    chunk_valid_sites = 0
    chunk_header_amount = 0
    chunk_acc_secheader_size = 0
    chunk_secheader_amount = 0
    header_min = math.inf
    header_max = 0
    header_response_min = math.inf
    header_response_max = 0
    header_website_min = math.inf
    header_website_max = 0
    secheader_min = math.inf
    secheader_max = 0
    secheader_response_min = math.inf
    secheader_response_max = 0
    secheader_website_min = math.inf
    secheader_website_max = 0

    top_secheaders = []
    top_responses = []
    top_websites = []


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
                        website_header_size = 0
                        website_secheader_size = 0
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
                            response_header_size = 0
                            response_secheader_size = 0
                            for header in headers:
                                header_size = calculate_header_size(header, headers[header])
                                response_header_size += header_size
                                if header_size < header_min:
                                    header_min = header_size
                                if header_size > header_max:
                                    header_max = header_size
                                chunk_acc_header_size += header_size
                                chunk_header_amount += 1
                                if header.lower() in security_headers:
                                    response_secheader_size += header_size
                                    if header_size < secheader_min:
                                        secheader_min = header_size
                                    if header_size > secheader_max:
                                        secheader_max = header_size
                                    top_secheaders.append(header_size)
                                    chunk_acc_secheader_size += header_size
                                    chunk_secheader_amount += 1
                            if response_header_size < header_response_min:
                                header_response_min = response_header_size
                            if response_header_size > header_response_max:
                                header_response_max = response_header_size
                            if response_secheader_size < secheader_response_min:
                                secheader_response_min = response_secheader_size
                            if response_secheader_size > secheader_response_max:
                                secheader_response_max = response_secheader_size
                            top_responses.append(response_secheader_size)
                            website_header_size += response_header_size
                            website_secheader_size += response_secheader_size
                            chunk_total_responses += 1
                        if website_secheader_size > secheader_website_max:
                            secheader_website_max = website_secheader_size
                        top_websites.append(website_secheader_size)
                        if website_secheader_size < secheader_website_min:
                            secheader_website_min = website_secheader_size
                        if website_header_size > header_website_max:
                            header_website_max = website_header_size
                        if website_header_size < header_website_min:
                            header_website_min = website_header_size
            if counter == CHUNK_SIZE:
                acc_header_size.append(chunk_acc_header_size)
                total_responses.append(chunk_total_responses)
                valid_sites.append(chunk_valid_sites)
                header_amount.append(chunk_header_amount)
                acc_secheader_size.append(chunk_acc_secheader_size)
                secheader_amount.append(chunk_secheader_amount)
                counter = 0
                chunk_acc_header_size = 0
                chunk_total_responses = 0
                chunk_valid_sites = 0
                chunk_acc_secheader_size = 0
                chunk_secheader_amount = 0
                chunk_header_amount = 0
    print(acc_header_size)
    print(total_responses)
    print(valid_sites)
    print(header_amount)
    print(acc_secheader_size)
    print(secheader_amount)
    print(f'header min: {header_min}')
    print(f'header max: {header_max}')
    print(f'header response min: {header_response_min}')
    print(f'header response max: {header_response_max}')
    print(f'header website min: {header_website_min}')
    print(f'header website max: {header_website_max}')
    print(f'secheader min: {secheader_min}')
    print(f'secheader max: {secheader_max}')
    print(f'secheader response min: {secheader_response_min}')
    print(f'secheader response max: {secheader_response_max}')
    print(f'secheader website min: {secheader_website_min}')
    print(f'secheader website max: {secheader_website_max}')
    top_secheaders.sort(reverse=True)
    top_responses.sort(reverse=True)
    top_websites.sort(reverse=True)
    print(top_secheaders[0:100])
    print(top_responses[0:100])
    print(top_websites[0:100])
    



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