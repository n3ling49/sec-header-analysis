import sys
import os
import json
import math
import time
import eval_utils

def get_total_header_count(headers, req_res_err_headers, key, security_headers):
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

def evaluate(results_folder):

    start_time = time.time()
    if not results_folder:
        print("No results directory given")
        exit()
    #print(results)

    headers = dict()
    errors = dict()
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, '../../results/'+results_folder)

    subdirs = os.listdir(results_dir)
    #print(subdirs)

    valid_site_amount = 0
    accumulated_average_requests_per_domain = 0
    total_requests = 0
    total_responses = 0
    total_header_length = 0
    sec_header_length = dict()
    total_all_response_headers_length = 0
    total_response_sec_header_length = 0
    domain_headers = dict()

    multiple_requests = dict()
    multiple_request_domains = dict() #to determine frequently contacted domains

    security_headers = []
    headers_dir = os.path.join(this_dir, '../../resources/securityheaders.json')
    with open(headers_dir) as file:
        security_headers = json.loads(file.read())["headers"]

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
                    with open(os.path.join(results_dir, dir, subdir, file)) as json_file:
                        data = None
                        try:
                            data = list(json.loads(json_file.read()))
                        except:
                            print("Error reading file: "+os.path.join(results_dir, dir, subdir, file))
                            continue
                        valid_set = False
                        request_amt = 0
                        req_per_domain = dict()
                        if len(data) > 0 and "error" in data[0]:
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
                            obj = dict()
                            for key in keys:
                                if key != "error" and type(req_res_err[key]) == str:
                                    try:
                                        obj[key] = json.loads(req_res_err[key])
                                    except:
                                        print(website_name)
                                        print(subdir)
                                        raise Exception("Error in json.loads")
                                else:
                                    obj[key] = req_res_err[key]
                            req_res_err = obj
                            for key in keys:
                                if key == "error":
                                    continue
                                req_res_err_obj = req_res_err[key]
                                if key == "request":
                                    request_amt += 1
                                    domain = eval_utils.extract_domain(req_res_err_obj["url"])
                                    if domain in req_per_domain:
                                        req_per_domain[domain] += 1
                                    else:
                                        req_per_domain[domain] = 1
                                    is_initial_request = False
                                    try:
                                        is_initial_request = eval_utils.is_initial_request(req_res_err_obj, website_name)
                                    except:
                                        print(subdir)
                                        raise Exception("Error in is_initial_request")
                                    if is_initial_request:
                                        try:
                                            initial_headers = eval_utils.find_initial_response(obj, data, website_name)["headers"]
                                        except:
                                            print(subdir)
                                            raise Exception("Error in find_initial_headers")
                                        if initial_headers:
                                            if not dir in domain_headers:
                                                domain_headers[dir] = dict()
                                            domain_headers[dir][website_name] = initial_headers
                                if key == "response":
                                    total_responses += 1
                                    total_all_response_headers_length += len(str(req_res_err_obj["headers"]))
                                    for header in req_res_err_obj["headers"]:
                                       if header in security_headers:
                                           #print(str(req_res_err_obj["headers"][header]))
                                           #raise Exception("stop")
                                           header_length = len(req_res_err_obj["headers"][header])
                                       #if not header in total_response_sec_header_length:
                                       #    total_response_sec_header_length[header] = header_length
                                           total_response_sec_header_length+=header_length
                                headers = get_total_header_count(headers, req_res_err_obj["headers"].keys(), key, security_headers)
                                for header in req_res_err_obj["headers"]:
                                    if header in security_headers:
                                        total_header_length += len(req_res_err_obj["headers"][header])
                                        if not header in sec_header_length:
                                            sec_header_length[header] = 0
                                        sec_header_length[header]+=len(req_res_err_obj["headers"][header])
                        domain_amount = len(req_per_domain.keys())

                        #count multiple requests per domain. Only exact matches. Subdomains each count as a separate domain.
                        for domain in req_per_domain:
                            request_amount = req_per_domain[domain]
                            if request_amount > 1:
                                if request_amount in multiple_requests:
                                    multiple_requests[request_amount] += 1
                                else:
                                    multiple_requests[request_amount] = 1
                                if domain in multiple_request_domains:
                                    multiple_request_domains[domain] += 1
                                else:
                                    multiple_request_domains[domain] = 1
                        
                        if domain_amount > 0:
                            average_req_per_domain = request_amt / domain_amount
                            accumulated_average_requests_per_domain += average_req_per_domain
                        total_requests += request_amt
    
    retVal = dict()
    retVal["total_requests"] = total_requests
    retVal["total_responses"] = total_responses
    retVal["total_header_length"] = total_header_length
    retVal["valid_site_amount"] = valid_site_amount
    retVal["accumulated_average_requests_per_domain"] = accumulated_average_requests_per_domain
    retVal["security_headers"] = security_headers
    retVal["headers"] = headers
    retVal["errors"] = errors
    retVal["multiple_requests"] = multiple_requests
    retVal["multiple_request_domains"] = multiple_request_domains
    retVal["sec_header_length"] = sec_header_length
    retVal["total_all_response_headers_length"] = total_all_response_headers_length
    retVal["total_response_sec_header_length"] = total_response_sec_header_length
    retVal["domain_headers"] = domain_headers
    
    end_time = time.time()
    print(str(end_time - start_time))
    return retVal

def request_findings(retVal):
    print(f'Total amount of requests: {retVal["total_requests"]}')
    print(f'Total amount of responses: {retVal["total_responses"]}')
    print(f'Response ratio: {round((retVal["total_responses"] / retVal["total_requests"]) * 100, 2)}%')

def header_distribution(retVal):
    total_reqs_and_res = retVal["total_requests"] + retVal["total_responses"]
    total_sec_headers = 0
    secheader_in_response_percentage = 0
    total_response_sec_headers = 0
    avg_single_response_secheader_size = 0
    for header in retVal["headers"]:
        for key in retVal["headers"][header]:
            total_sec_headers += retVal["headers"][header][key]
            if key == "response":
                total_response_sec_headers+=retVal["headers"][header][key]
    for header in retVal["headers"]:
        header_amount = 0
        for key in retVal["headers"][header]:
            header_amount += retVal["headers"][header][key]
        message = f'{header}: {header_amount}'
        if total_sec_headers > 0:
            message += f' ({round((header_amount / total_sec_headers) * 10000) / 100 }% of all security headers set)'
        print(message)
        if "request" in retVal["headers"][header]:
            print(f' ({retVal["headers"][header]["request"]} requests; {round((retVal["headers"][header]["request"] / retVal["total_requests"]) * 10000) / 100 }% of all requests)')
        else:
            print(f' (0 requests; 0% of all requests)')
        if "response" in retVal["headers"][header]:
            response_percentage = round((retVal["headers"][header]["response"] / retVal["total_responses"]) * 100, 2)
            secheader_in_response_percentage+=response_percentage
            avg_single_response_secheader_size+=(retVal["sec_header_length"][header]/retVal["headers"][header]["response"])*(retVal["headers"][header]["response"]/total_response_sec_headers)
            print(f' ({retVal["headers"][header]["response"]} responses; { response_percentage }% of all responses)')
        else:
            print(f' (0 responses; 0% of all responses)')
        print(f' ({round((header_amount / total_reqs_and_res) * 100, 2)}% of all requests/responses)')
        print()
        if header in retVal["security_headers"] and "response" in retVal["headers"][header].keys():
            print(f'Average response value size: {retVal["sec_header_length"][header]/retVal["headers"][header]["response"]}')
            print()
    print(f'total length of all response headers: {retVal["total_all_response_headers_length"]}')
    print(f'avg. length of response headers: {retVal["total_all_response_headers_length"]/retVal["total_responses"]}')
    print(f'sec headers per response: {secheader_in_response_percentage/100}')
    print(f'total length of all response security headers: {retVal["total_response_sec_header_length"]}')
    print(f'avg. length of response security headers: {retVal["total_response_sec_header_length"]/retVal["total_responses"]}')
    print(f'avg. length of one single security header: {avg_single_response_secheader_size}')
    return total_sec_headers

def multiple_requests(retVal):
    print("Multiple requests per domain:")
    multiple_request_keys = list(retVal["multiple_requests"].keys())
    multiple_request_keys.sort()
    total_times_multiple_requests = 0
    for request_amount in multiple_request_keys:
        total_times_multiple_requests += retVal["multiple_requests"][request_amount]
    print(f'Total times requests were sent multiple times to the same domain (2+ times): {total_times_multiple_requests} ({round((total_times_multiple_requests / retVal["valid_site_amount"]) * 100, 2)}% of all sites, where at least 1 response was recorded)')
    for request_amount in multiple_request_keys:
        print(f'{request_amount} times: {retVal["multiple_requests"][request_amount]}')
    
    most_requested_domains = sorted(retVal["multiple_request_domains"].items(), key=lambda x: x[1], reverse=True)[0:50]
    print("Most frequently contacted domains:")
    for domain in most_requested_domains:
        print(f'{domain[0]}: {domain[1]}')

def other(retVal, total_sec_headers):
    print("Total length of security headers content: "+str(retVal["total_header_length"]))
    print(retVal["errors"])
    if retVal["valid_site_amount"] > 0:
        print("Average requests per Domain per Website: "+str(retVal["accumulated_average_requests_per_domain"] / retVal["valid_site_amount"]))
    if retVal["total_requests"] > 0:
        print(f'Average amount of sec-headers set per request: {total_sec_headers / retVal["total_requests"]}')

def initial_headers(retVal):
    for dir in retVal["domain_headers"]:
        initial_sec_headers = dict()
        print(f'{dir}:')
        for domain in retVal["domain_headers"][dir]:
            for header in retVal["domain_headers"][dir][domain]:
                if not header in retVal["security_headers"]:
                    continue
                if not header in initial_sec_headers:
                    initial_sec_headers[header] = 1
                else:
                    initial_sec_headers[header] += 1
        for header in initial_sec_headers:
            print(f'{header}: {initial_sec_headers[header]}')
        print()