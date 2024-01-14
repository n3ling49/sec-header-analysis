import os
import json
import eval_utils

deprecated_headers = [
    "expect-ct",
    "x-frame-options",
    "x-xss-protection",
    "public-key-pins",
]

info_revealing_headers = [
    "server",
    "x-aspnet-version",
    "x-aspnetmvc-version",
    "x-powered-by",
]

recommended_headers = [
    "permissions-policy",
    "cross-origin-embedder-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    "x-content-security-policy",
    "content-security-policy",
    "strict-transport-security",
    "referrer-policy",
    "content-type",
    "x-content-type-options",
    "x-dns-prefetch-control",
    "access-control-allow-origin",
    "x-permitted-cross-domain-policies",
    "content-security-policy-report-only",
]

CHUNK_SIZE = 4

def find_security_headers(initial=False, follow_redirects=False):
    results_folder = "ba_dataset/"
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, '../../results/'+results_folder)

    security_headers = []
    headers_dir = os.path.join(this_dir, '../../resources/securityheaders.json')
    with open(headers_dir) as file:
        security_headers = json.loads(file.read())["headers"]

    other_headers = []

    subdirs = os.listdir(results_dir)
    initial_response_fail = 0
    missing_response = 0
    wrong_status = 0
    chunks = []

    chunk_id = 0

    chunk = dict()
    chunk["recommended"] = dict()
    for header in recommended_headers:
        chunk["recommended"][header] = 0
    chunk["deprecated"] = dict()
    for header in deprecated_headers:
        chunk["deprecated"][header] = 0
    chunk["info_revealing"] = dict()
    for header in info_revealing_headers:
        chunk["info_revealing"][header] = 0
    chunk["others"] = dict()
    for header in security_headers:
        if not header in chunk["recommended"] and not header in chunk["deprecated"] and not header in chunk["info_revealing"]:
            chunk["others"][header] = 0
            other_headers.append(header)
    chunk["valid_responses"] = 0
    chunk["ids"] = []
    chunks.append(chunk)

    chunk_counter = 0
    subdirs.sort(key=eval_utils.sortfunc)
    for dir in subdirs:
        sub_subdirs = os.listdir(os.path.join(results_dir, dir))
        #print(sub_subdirs)

        print(dir)
        sub_subdirs.sort(key=eval_utils.sortfunc)
        for subdir in sub_subdirs:
            files = os.listdir(os.path.join(results_dir, dir, subdir))
            chunk["ids"].append(chunk_id)
            #print(files)
            #print(subdir)
            for file in files:
                website_name = file.split(".json")[0]
                with open(os.path.join(results_dir, dir, subdir, file), "r") as f:
                    data = None
                    try:
                        data = list(json.load(f))
                    except:
                        print(f'error in {subdir}/{file}')
                        continue
                    if not initial:
                        is_valid = False
                        for req_res_err in data:
                            if type(req_res_err) == str:
                                req_res_err = json.loads(req_res_err)
                            if not "request" in req_res_err:
                                continue
                            if type(req_res_err["request"]) == str:
                                req_res_err["request"] = json.loads(req_res_err["request"])
                            if not "response" in req_res_err:
                                continue
                            response = None
                            if eval_utils.is_initial_request(req_res_err["request"], website_name):
                                response = eval_utils.find_initial_response(req_res_err, data, website_name)
                            else:
                                continue
                            if response is None:
                                break
                            if type(response) == str:
                                response = json.loads(response)
                            if str(response["status_code"])[0] == "4":
                                break
                            is_valid = True
                            break
                        if not is_valid:
                            continue


                    for req_res_err in data:
                        if type(req_res_err) == str:
                            req_res_err = json.loads(req_res_err)
                        if not "request" in req_res_err:
                            continue
                        if type(req_res_err["request"]) == str:
                            req_res_err["request"] = json.loads(req_res_err["request"])
                        if not "response" in req_res_err:
                            missing_response += 1
                            continue
                        response = req_res_err["response"]
                        if initial:
                            if not eval_utils.is_initial_request(req_res_err["request"], website_name):
                                continue
                            if follow_redirects:
                                response = eval_utils.find_initial_response(req_res_err, data, website_name)
                                if response is None:
                                    initial_response_fail += 1
                                    break
                        if type(response) == str:
                            response = json.loads(response)
                        
                        if initial and str(response["status_code"])[0] == "4":
                            wrong_status += 1
                            break
                        headers = response["headers"]
                        if type(headers) == str:
                            headers = json.loads(headers)
                        if chunk_counter == CHUNK_SIZE:
                            chunk_counter = 0
                            chunk = dict()
                            chunk["recommended"] = dict()
                            for header in recommended_headers:
                                chunk["recommended"][header] = 0
                            chunk["deprecated"] = dict()
                            for header in deprecated_headers:
                                chunk["deprecated"][header] = 0
                            chunk["info_revealing"] = dict()
                            for header in info_revealing_headers:
                                chunk["info_revealing"][header] = 0
                            chunk["others"] = dict()
                            for header in other_headers:
                                chunk["others"][header] = 0
                            chunk["valid_responses"] = 0
                            chunk["ids"] = []
                            chunks.append(chunk)
                        for header in headers:
                            header = header.lower()
                            if header in chunks[-1]["recommended"]:
                                chunks[-1]["recommended"][header] += 1
                            elif header in chunks[-1]["deprecated"]:
                                chunks[-1]["deprecated"][header] += 1
                            elif header in chunks[-1]["info_revealing"]:
                                chunks[-1]["info_revealing"][header] += 1
                            elif header in chunks[-1]["others"]:
                                chunks[-1]["others"][header] += 1
                        chunks[-1]["valid_responses"] += 1
                        if initial:
                            break
            chunk_counter += 1
            chunk_id += 1
    open("headers.txt", "w").write(str(chunks))
    print(f'initial response fails: {initial_response_fail}')
    print(f'missing responses: {missing_response}')
    print(f'wrong status: {wrong_status}')
    print(f'valid responses: {sum([chunk["valid_responses"] for chunk in chunks])}')
    return other_headers

def load_other_headers():
    other_headers = []
    with open("headers.txt", "r") as f:
        chunks = eval(f.read())
        for chunk in chunks:
            for header in chunk["others"]:
                if not header in other_headers:
                    other_headers.append(header)
    return other_headers

def print_sec_headers(other_headers):

    recommended_percentage = dict()
    for header in recommended_headers:
        recommended_percentage[header] = []
    deprecated_percentage = dict()
    for header in deprecated_headers:
        deprecated_percentage[header] = []
    info_revealing_percentage = dict()
    for header in info_revealing_headers:
        info_revealing_percentage[header] = []
    other_percentage = dict()
    for header in other_headers:
        other_percentage[header] = []

    with open("headers.txt", "r") as f:
        chunks = eval(f.read())

        for chunk in chunks:
            #print(chunk["ids"])
            #print("recommended:")
            #print(chunk["recommended"])
            #print("deprecated:")
            #print(chunk["deprecated"])
            #print("info_revealing:")
            #print(chunk["info_revealing"])
            #print("")
            #for header in chunk["recommended"]:
            #    recommended_percentage[header].append(round(chunk["recommended"][header]/chunk["valid_responses"],4))
            #for header in chunk["deprecated"]:
            #    deprecated_percentage[header].append(round(chunk["deprecated"][header]/chunk["valid_responses"],4))
            #for header in chunk["info_revealing"]:
            #    info_revealing_percentage[header].append(round(chunk["info_revealing"][header]/chunk["valid_responses"],4))
            #for header in chunk["others"]:
            #    other_percentage[header].append(round(chunk["others"][header]/chunk["valid_responses"],4))

            for header in chunk["recommended"]:
                recommended_percentage[header].append(chunk["recommended"][header])
            for header in chunk["deprecated"]:
                deprecated_percentage[header].append(chunk["deprecated"][header])
            for header in chunk["info_revealing"]:
                info_revealing_percentage[header].append(chunk["info_revealing"][header])
            for header in chunk["others"]:
                other_percentage[header].append(chunk["others"][header])
        print('===========================')
        print("RECOMMENDED:")
        print('===========================')
        for header in recommended_percentage:
            print(header)
            print(recommended_percentage[header])
        print('===========================')
        print("DEPRECATED:")
        print('===========================')
        for header in deprecated_percentage:
            print(header)
            print(deprecated_percentage[header])
        print('===========================')
        print("INFO REVEALING:")
        print('===========================')
        for header in info_revealing_percentage:
            print(header)
            print(info_revealing_percentage[header])
        print('===========================')
        print("OTHERS:")
        print('===========================')
        for header in other_percentage:
            print(header)
            print(other_percentage[header])

def convert_helme_data():
    chunks = []
    chunk_amt = int(1000/CHUNK_SIZE)
    print(chunk_amt)
    for i in range(0, int(1000/CHUNK_SIZE)):
        chunk = dict()
        chunk["recommended"] = dict()
        chunk["recommended"]["content-security-policy"] = 0
        chunk["valid_responses"] = 0
        chunks.append(chunk)
    with open("csp-sites.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.split(" ")[0].replace(",", "")
            rank = int(line)
            chunk_id = int((rank-1)//(CHUNK_SIZE*1000))
            chunks[chunk_id]["valid_responses"] += 1
            chunks[chunk_id]["recommended"]["content-security-policy"] += 1
    open("helme.txt", "w").write(str(chunks))


#find_security_headers(True, True)
#convert_helme_data()
#print_sec_headers()
print_sec_headers(find_security_headers())
#print_sec_headers(load_other_headers())