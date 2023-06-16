from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import utils
import threading
import math
import json

WEBSITEAMT = 16
def scanWebsites(result, websites, amt = WEBSITEAMT):
    options = Options()
    options.add_argument('--headless')
    #the following two arguments somehow fix the webdriver issue in docker
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    visited = 0
    while visited < amt:
        print("requesting nr. " + websites[visited].replace("\n", "").replace(",", ", ") + " ...")
        website = utils.get(websites[visited])
        result[website] = list()
        driver.get('https://www.' + website)
        print("Requests ("+ website +"): " + str(len(driver.requests)))

        for request in driver.requests:
            req_and_res = dict()

            request_json = {
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
            }

            req_and_res["request"] = json.dumps(request_json)

            if request.response:
                response_json = {
                    "status_code": request.response.status_code,
                    "reason": request.response.reason,
                    "headers": dict(request.response.headers),
                }
                req_and_res["response"] = json.dumps(response_json)

            result[website].append(req_and_res)

        del driver.requests
        visited += 1
    driver.close()

"""
Efficiently accesses websites included in 'websites' list by using 'threadAmt' amount of threads.
Also saves every occurring https request per website in a dictionary, which the function then returns.
"""
def multiScan(websites, threadAmt):
    result = dict()

    threads = list()
    websites_per_thread = math.ceil(int(WEBSITEAMT / threadAmt))
    for i in range(0, threadAmt):
        start_website_index = i * websites_per_thread
        stop_website_index = (i + 1) * websites_per_thread
        thread = threading.Thread(target=scanWebsites, args=(result, websites[start_website_index:stop_website_index], websites_per_thread))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    return result