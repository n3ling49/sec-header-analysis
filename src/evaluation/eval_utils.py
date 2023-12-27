import json

def extract_clean_domain(url):
    domain = extract_domain(url)
    clean_domain = domain.split('.')[-2]
    return clean_domain

def extract_domain(url):
    domain = url.split("/")[2]
    return domain

def is_initial_request(request, domain):
    try:
        if request["method"] == "GET" and (request["url"] == f"https://{domain}/" or request["url"] == f"http://{domain}/"):
            return True
    except:
        print(request)
        print(domain)
        raise Exception("Error in is_initial_request")
    return False

def find_initial_response(initial_req_res_err, req_res_err_arr, domain):
    #print(initial_req_res_err)
    #print(type(initial_req_res_err["request"]))
    if not is_initial_request(initial_req_res_err["request"], domain):
        return None
    if not "response" in initial_req_res_err:
        return None
    response = initial_req_res_err["response"]
    if type(response) == str:
        response = json.loads(response)
    status = response["status_code"]
    counter = 0
    last_index = 0
    while str(status)[0] == "3":
        if not ("location" in response["headers"] or "Location" in response["headers"]):
            return None
        if counter > len(req_res_err_arr):
            return None
        iterator = 0
        for req_res_err in req_res_err_arr[last_index+1:]:
            #req_res_err = json.loads(req_res_err)
            if not "request" in req_res_err:
                continue
            if type(req_res_err["request"]) == str:
                req_res_err["request"] = json.loads(req_res_err["request"])
            #print(response)
            location = None
            try:
                location = response["headers"]["Location"]
            except:
                location = response["headers"]["location"]

            if req_res_err["request"]["url"] == location:
                if not "response" in req_res_err: #manchmal geht der redirect mit https nicht aber mit http. TODO?
                    return None
                try:
                    response = json.loads(req_res_err["response"])
                except:
                    print(domain)
                    raise Exception("Error in find_initial_headers")
                if type(response["headers"]) == str:
                    response["headers"] = json.loads(response["headers"])
                status = response["status_code"]
                break
            iterator += 1
        if iterator == len(req_res_err_arr):
            return None
        last_index = iterator
        counter += 1
    return response
