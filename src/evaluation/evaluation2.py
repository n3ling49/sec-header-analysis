import os
import json
import eval_utils

def success():
    results_folder = "ba_dataset/"
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, '../../results/'+results_folder)

    subdirs = os.listdir(results_dir)

    success_percentage = dict()
    dir_counter = 0
    for dir in subdirs:
        sub_subdirs = os.listdir(os.path.join(results_dir, dir))
        #print(sub_subdirs)
        print(dir)
        subdir_counter = 0
        success_counter = 0
        for subdir in sub_subdirs:
            files = os.listdir(os.path.join(results_dir, dir, subdir))
            #print(files)
            #print(subdir)
            success_counter += len(files)
            if subdir_counter == 49:
                success_percentage[f'{dir_counter*100000+1}-{dir_counter*100000+50000}'] = success_counter/50000
                success_counter = 0
            elif subdir_counter == 99:
                success_percentage[f'{dir_counter*100000+50001}-{dir_counter*100000+100000}'] = success_counter/50000
                success_counter = 0
            subdir_counter += 1
        dir_counter += 1
    for key in success_percentage.keys():
        print(f'{key}: {success_percentage[key]}')
    print(str(success_percentage.keys()))
    print(str(success_percentage.values()))

def initial_status_codes(initial=False, follow_redirects=False):
    results_folder = "ba_dataset/"
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, '../../results/'+results_folder)

    subdirs = os.listdir(results_dir)
    initial_response_fail = 0
    missing_response = 0
    status_codes = dict()
    for dir in subdirs:
        sub_subdirs = os.listdir(os.path.join(results_dir, dir))
        #print(sub_subdirs)
        print(dir)
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
                                response = eval_utils.find_initial_response(req_res_err, data, website_name)
                                if response is None:
                                    initial_response_fail += 1
                                    break
                        if type(response) == str:
                            response = json.loads(response)
                        status_code = str(response["status_code"])
                        if not status_code in status_codes:
                            print(status_code)
                            status_codes[status_code] = 1
                        else:
                            status_codes[status_code] += 1
                        if initial:
                            break
    open("codes.txt", "w").write(str(status_codes))
    print(f'initial response fails: {initial_response_fail}')
    print(f'missing responses: {missing_response}')

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

initial_status_codes(True, True)
with open("codes.txt", "r") as f:
    status_codes = eval(f.read())
    print_status_codes(status_codes)