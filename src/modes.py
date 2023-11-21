from selenium.common.exceptions import TimeoutException
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
import utils as utils
import json
import traceback
import multiprocessing
from filelock import FileLock

def scanWebsites(result, website_queue, thread_nr):

    while True:
        options = ChromeOptions()
        options.add_argument('--headless')
        #the following two arguments somehow fix the webdriver issue in docker
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        #the following argument is needed to access websites with invalid certificates
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-gpu')
        #the following argument is needed to hide headless chrome
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        
        driver = None
        file = "/usr/bin/chromedriver"
        lockfile = "/usr/bin/chromedriver.lock"
        lock = FileLock(lockfile)
        lock.acquire()
        try:
            driver = Chrome(options=options)
        finally:
            lock.release()
        driver.set_page_load_timeout(60)

        item = website_queue.get()

        if item is None:
            break
        
        print("requesting nr. " + item.replace("\n", "").replace(",", ", ") + " (Thread "+str(thread_nr+1)+")...")
        website_nr = item.split(",")[0]
        website = utils.get(item)
        website_result = list()

        try:
            driver.get('https://' + website)
            print("Requests ("+ website +"): " + str(len(driver.requests)))

            if len(driver.requests) == 0:
                driver.get('http://' + website)
                print("Requests HTTP ("+ website +"): " + str(len(driver.requests)))

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
                
                website_result.append(req_and_res)
        except Exception as e:
            print(f'caught {type(e)}: e')
            if not type(e) == TimeoutException:
                traceback.print_exc()
            website_result.append({
                "error": f'{type(e)}'
            })
        
        utils.save_single_file(website_result, website, "", website_nr)
        result[website] = website_result

        del driver.requests
    driver.close()

"""
Efficiently accesses websites included in 'websites' list by using 'threadAmt' amount of threads.
Also saves every occurring https request per website in a dictionary, which the function then returns.
"""
def multiScan(websites, threadAmt):

    manager = multiprocessing.Manager()
    q = manager.Queue()
    result = manager.dict()

    for website in websites:
        q.put(website)
    for i in range(0, threadAmt):
        q.put(None)

    threads = list()
    for i in range(0, threadAmt):
        #thread = threading.Thread(target=scanWebsites, args=(result, q, i))
        #threads.append(thread)
        process = multiprocessing.Process(target=scanWebsites, args=(result, q, i))
        process.start()
        threads.append(process)

    for process in threads:
        process.join()
    return dict(result)