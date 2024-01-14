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

def sortfunc(s):
    return int(s.split('-')[0])

def find_initial_response(initial_req_res_err, req_res_err_arr, domain, feedback=False):
    #print(initial_req_res_err)
    #print(type(initial_req_res_err["request"]))
    if type(initial_req_res_err["request"]) == str:
        initial_req_res_err["request"] = json.loads(initial_req_res_err["request"])
    if not is_initial_request(initial_req_res_err["request"], domain):
        #request is not initial request
        #no initial request
        if feedback:
            return -1
        return None
    if not "response" in initial_req_res_err:
        #initial request has no response
        #no response
        if feedback:
            return -2
        return None
    response = initial_req_res_err["response"]
    if type(response) == str:
        response = json.loads(response)
    status = response["status_code"]
    counter = 0
    last_index = 0
    while str(status)[0] == "3":
        if not ("location" in response["headers"] or "Location" in response["headers"]):
            #no redirect url found
            #no url
            if feedback:
                return -3
            return None
        if counter > len(req_res_err_arr):
            #all requests have been investigated without success
            #next request missing
            if feedback:
                return -4
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
                    #request within redirect chain had no response
                    #no response
                    if feedback:
                        return -2
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
            #final response was not found
            #next request missing
            if feedback:
                return -4
            return None
        last_index = iterator
        counter += 1
    return response
