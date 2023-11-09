import sys
import os
import json
import math

def get_total_header_count(headers, req_res_err_headers, key):
    for header in req_res_err_headers:
        if not header in security_headers:
            continue
        if header in headers:
            if key in headers[header]:
                headers[header][key] += 1
            else:
                headers[header][key] = 1
        else:
            headers[header] = dict()
            headers[header][key] = 1
    return headers

results = sys.argv[1]
if not results:
    print("No results directory given")
    exit()
#print(results)

headers = dict()
errors = dict()
this_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(this_dir, '../../results/'+results)

subdirs = os.listdir(results_dir)
#print(subdirs)

valid_site_amount = 0
accumulated_average_requests_per_domain = 0
total_requests = 0
total_responses = 0
total_header_length = 0

security_headers = []
headers_dir = os.path.join(this_dir, '../../resources/securityheaders.json')
with open(headers_dir) as file:
    security_headers = json.loads(file.read())["headers"]

for dir in subdirs:
    sub_subdirs = os.listdir(os.path.join(results_dir, dir))
    #print(sub_subdirs)
    for subdir in sub_subdirs:
        files = os.listdir(os.path.join(results_dir, dir, subdir))
        #print(files)
        for file in files:
            if file.endswith(".json"):
                website_name = file.split(".json")[0]
                with open(os.path.join(results_dir, dir, subdir, file)) as json_file:
                    data = list(json.loads(json_file.read()))
                    valid_set = False
                    request_amt = 0
                    req_per_domain = dict()
                    if "error" in data[0]:
                        if data[0]["error"] in errors:
                            errors[data[0]["error"]] += 1
                        else:
                            errors[data[0]["error"]] = 1
                        continue
                    for req_res_err in data:
                        if not valid_set:
                            valid_set = True
                            valid_site_amount += 1
                        keys = req_res_err.keys()
                        for key in keys:
                            if key == "error":
                                continue
                            req_res_err_obj = json.loads(req_res_err[key])
                            if key == "request":
                                request_amt += 1
                                domain = req_res_err_obj["url"].split("/")[2]
                                if domain in req_per_domain:
                                    req_per_domain[domain] += 1
                                else:
                                    req_per_domain[domain] = 1
                            if key == "response":
                                total_responses += 1
                            headers = get_total_header_count(headers, req_res_err_obj["headers"].keys(), key)
                            for header in req_res_err_obj["headers"]:
                                if header in security_headers:
                                    total_header_length += len(req_res_err_obj["headers"][header])
                    domain_amount = len(req_per_domain.keys())
                    if domain_amount > 0:
                        average_req_per_domain = request_amt / domain_amount
                        accumulated_average_requests_per_domain += average_req_per_domain
                    total_requests += request_amt

print(f'Total amount of requests: {total_requests}')
print(f'Total amount of responses: {total_responses}')
print(f'Response ratio: {round((total_responses / total_requests) * 100, 2)}%')
print()
total_reqs_and_res = total_requests + total_responses
total_sec_headers = 0
for header in headers:
    for key in headers[header]:
        total_sec_headers += headers[header][key]
for header in headers:
    header_amount = 0
    for key in headers[header]:
        header_amount += headers[header][key]
    message = f'{header}: {header_amount}'
    if total_sec_headers > 0:
        message += f' ({round((header_amount / total_sec_headers) * 10000) / 100 }% of all security headers set)'
    print(message)
    if "request" in headers[header]:
        print(f' ({headers[header]["request"]} requests; {round((headers[header]["request"] / total_requests) * 10000) / 100 }% of all requests)')
    else:
        print(f' (0 requests; 0% of all requests)')
    if "response" in headers[header]:
        print(f' ({headers[header]["response"]} responses; {round((headers[header]["response"] / total_responses) * 100, 2) }% of all responses)')
    else:
        print(f' (0 responses; 0% of all responses)')
    print(f' ({round((header_amount / total_reqs_and_res) * 100, 2)}% of all requests/responses)')
    print()
print("Total length of security headers content: "+str(total_header_length))
print(errors)
if valid_site_amount > 0:
    print("Average requests per Domain per Website: "+str(accumulated_average_requests_per_domain / valid_site_amount))
if total_requests > 0:
    print(f'Average amount of sec-headers set per request: {total_sec_headers / total_requests}')