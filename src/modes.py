from selenium.common.exceptions import TimeoutException
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
import utils as utils
import json
import traceback
import multiprocessing
from filelock import FileLock
import os

def scanWebsites(result, website_queue, thread_nr):
    print('cloning executable for thread '+str(thread_nr+1)+'...')
    utils.init_process_dir(thread_nr)
    while True:
        try:
            options = ChromeOptions()
            options.add_argument('--headless=new')
            #the following two arguments somehow fix the webdriver issue in docker
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            #the following argument is needed to access websites with invalid certificates
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-application-cache')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--incognito')
            #the following argument is needed to hide headless chrome
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument('--user-data-dir=/app/processdata/PROFILE'+str(thread_nr))
            
            driver = None
            #file = "/usr/bin/chromedriver"
            #lockfile = "/usr/bin/chromedriver.lock"
            #lock = FileLock(lockfile)
            #lock.acquire()
            #try:
            driver = Chrome(driver_executable_path='/app/processdata/PROFILE'+str(thread_nr)+'/chromedriver', version_main=119, options=options)
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonCookie'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonCookie')
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonPreferences'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonPreferences')
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonLock'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonLock')
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonSocket'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonSocket')
            #finally:
            #    lock.release()
            driver.set_page_load_timeout(60)

            item = website_queue.get()

            if item is None:
                print(str(thread_nr+1) + ' finished')
                break
            
            print("requesting nr. " + item.replace("\n", "").replace(",", ", ") + " (Thread "+str(thread_nr+1)+")...")
            website_nr = item.split(",")[0]
            website = utils.get(item)
            website_result = list()

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
        
            utils.save_single_file(website_result, website, "", website_nr)
            result[website] = website_result

            del driver.requests
            driver.quit()
        except Exception as e:
            print(f'(Thread {thread_nr}) caught {type(e)}: e')
            if not type(e) == TimeoutException:
                traceback.print_exc()
            website_result.append({
                "error": f'{type(e)}'
            })

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