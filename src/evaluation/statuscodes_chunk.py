import os
import json
import eval_utils

CHUNK_SIZE = 4

def initial_status_codes(initial=True, follow_redirects=True):
    results_folder = "ba_dataset/"
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, '../../results/'+results_folder)

    subdirs = os.listdir(results_dir)
    initial_response_fail = 0
    missing_response = 0
    status_codes = dict()
    initial_errors = dict()
    initial_errors["noinitial"] = 0
    initial_errors["noresponse"] = 0
    initial_errors["nourl"] = 0
    initial_errors["norequest"] = 0
    norequestsites = []
    forbidden_chunks = []
    chunk_counter = 0
    forbidden_amt = 0

    subdirs.sort(key=eval_utils.sortfunc)
    for dir in subdirs:
        sub_subdirs = os.listdir(os.path.join(results_dir, dir))
        #print(sub_subdirs)
        print(dir)
        sub_subdirs.sort(key=eval_utils.sortfunc)
        for subdir in sub_subdirs:
            files = os.listdir(os.path.join(results_dir, dir, subdir))
            #print(files)
            #print(subdir)
            for file in files:
                website_name = file.split(".json")[0]
                with open(os.path.join(results_dir, dir, subdir, file), "r") as f:
                    data = list(json.load(f))
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
                                response = eval_utils.find_initial_response(req_res_err, data, website_name, True)
                                if type(response) == int:
                                    initial_response_fail += 1
                                    break
                        if type(response) == str:
                            response = json.loads(response)
                        status_code = str(response["status_code"])
                        if status_code == "403":
                            forbidden_amt += 1
                        if initial:
                            break
            chunk_counter += 1
            if chunk_counter == CHUNK_SIZE:
                forbidden_chunks.append(forbidden_amt)
                forbidden_amt = 0
                chunk_counter = 0

    print(forbidden_chunks)                    
    #open("codes.txt", "w").write(str(status_codes))
    #print(f'initial response fails: {initial_response_fail}')
    #print(f'missing responses: {missing_response}')
    #for key in initial_errors.keys():
    #    print(f'{key}: {initial_errors[key]}')
    #for site in norequestsites[0:100]:
    #    print(site)

def print_status_codes(status_codes):
    codes = list(status_codes.keys())
    codes.sort()
    total_responses = 0
    total_category = 0
    for i in range(len(codes)):
        start_nr = int(codes[i][0])
        if i == 0:
            if start_nr < 6:
                print(f'{start_nr}xx:')
            else:
                print('others:')
        elif i>0 and start_nr != int(codes[i-1][0]):
            if start_nr < 6:
                print()
                print(f'total: {total_category}')
                total_category = 0
                print()
                print(f'{start_nr}xx:')
            elif int(codes[i-1][0]) < 6:
                print()
                print(f'total: {total_category}')
                total_category = 0
                print()
                print('others:')
        code = codes[i]
        total_responses += status_codes[code]
        total_category += status_codes[code]
        print(f'{code}: {status_codes[code]}')
    print(f'total: {total_category}')
    print()
    print(f'total responses: {total_responses}')

initial_status_codes()