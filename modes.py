from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import utils
import threading
import math
import json
import queue

def scanWebsites(result, website_queue):
    options = Options()
    options.add_argument('--headless')
    #the following two arguments somehow fix the webdriver issue in docker
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    while True:
        item = website_queue.get()

        if item is None:
            break

        print("requesting nr. " + item.replace("\n", "").replace(",", ", ") + " ...")
        website = utils.get(item)
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
    driver.close()

"""
Efficiently accesses websites included in 'websites' list by using 'threadAmt' amount of threads.
Also saves every occurring https request per website in a dictionary, which the function then returns.
"""
def multiScan(websites, threadAmt):
    result = dict()

    q = queue.Queue()

    for website in websites:
        q.put(website)
    for i in range(0, threadAmt):
        q.put(None)

    threads = list()
    for i in range(0, threadAmt):
        thread = threading.Thread(target=scanWebsites, args=(result, q))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    return result