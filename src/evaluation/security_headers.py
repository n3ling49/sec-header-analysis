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

    subdirs = os.listdir(results_dir)
    initial_response_fail = 0
    missing_response = 0
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
    chunk["valid_responses"] = 0
    chunk["ids"] = []
    chunks.append(chunk)

    chunk_counter = 0
    for dir in subdirs:
        sub_subdirs = os.listdir(os.path.join(results_dir, dir))
        #print(sub_subdirs)

        print(dir)
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
                        chunks[-1]["valid_responses"] += 1
                        if initial:
                            break
            chunk_counter += 1
            chunk_id += 1
    open("headers.txt", "w").write(str(chunks))
    print(f'initial response fails: {initial_response_fail}')
    print(f'missing responses: {missing_response}')

def print_sec_headers():

    recommended_percentage = dict()
    for header in recommended_headers:
        recommended_percentage[header] = []
    deprecated_percentage = dict()
    for header in deprecated_headers:
        deprecated_percentage[header] = []
    info_revealing_percentage = dict()
    for header in info_revealing_headers:
        info_revealing_percentage[header] = []

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

            for header in chunk["recommended"]:
                recommended_percentage[header].append(chunk["recommended"][header])
            #for header in chunk["deprecated"]:
            #    deprecated_percentage[header].append(chunk["deprecated"][header])
            #for header in chunk["info_revealing"]:
            #    info_revealing_percentage[header].append(chunk["info_revealing"][header])
        print("recommended:")
        print(recommended_percentage)
        #print("deprecated:")
        #print(deprecated_percentage)
        #print("info_revealing:")
        #print(info_revealing_percentage)

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


find_security_headers(True, False)
#convert_helme_data()
print_sec_headers()