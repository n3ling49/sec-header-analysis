from selenium.common.exceptions import TimeoutException
#from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions
import utils as utils
import json
import traceback
import multiprocessing
import os
import logging
import time

def scanWebsites(result, website_queue, thread_nr, init_dir):
    if init_dir:
        logging.info('cloning executable for thread '+str(thread_nr+1)+'...')
        utils.init_process_dir(thread_nr)
    #counter = 0
    while True:
        try:
            #counter+=1
            #logging.info(f'Process {thread_nr+1} batch webiste count: {counter}')
            #logging.info(f'Process {thread_nr+1} running Threads: {threading.active_count()}')
            #logging.info(f'Process {thread_nr+1} RAM memory % used:', psutil.virtual_memory()[2])
            #ogging.info(f'Process {thread_nr+1} Active children: {len(multiprocessing.active_children())}')
            options = ChromeOptions()
            options.add_argument('--headless=new')
            #the following two arguments somehow fix the webdriver issue in docker
            #options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            #the following argument is needed to access websites with invalid certificates
            options.add_argument('--ignore-certificate-errors')
            #options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-application-cache')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--incognito')
            #the following argument is needed to hide headless chrome
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--user-data-dir=/app/processdata/PROFILE'+str(thread_nr))
            
            driver = None

            driver = Chrome(driver_executable_path='/app/processdata/PROFILE'+str(thread_nr)+'/chromedriver', version_main=119, options=options, use_subprocess=True)
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonCookie'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonCookie')
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonPreferences'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonPreferences')
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonLock'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonLock')
            if os.path.islink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonSocket'):
                os.unlink('/app/processdata/PROFILE'+str(thread_nr)+'/SingletonSocket')

            driver.set_page_load_timeout(60)

            del driver.requests
            item = website_queue.get()

            if item is None:
                break
            
            logging.info("requesting nr. " + item.replace("\n", "").replace(",", ", ") + " (Thread "+str(thread_nr+1)+")...")
            website_nr = item.split(",")[0]
            website = utils.get(item)
            website_result = list()

            driver.get('https://' + website)
            logging.info("Requests ("+ website +"): " + str(len(driver.requests)))

            if len(driver.requests) < 2:
                del driver.requests
                driver.get('http://' + website)
                logging.info("Requests HTTP ("+ website +"): " + str(len(driver.requests)))

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

            driver.quit()
        except Exception as e:
            if not type(e) == TimeoutException:
                logging.exception(f'(Thread {thread_nr+1}) caught {type(e)}: e')
                traceback.print_exc()
            else:
                logging.info(f'(Thread {thread_nr+1}) caught {type(e)}: e')
            website_result.append({
                "error": f'{type(e)}'
            })
            utils.save_single_file(website_result, website, "", website_nr)
            result[website] = website_result

            driver.quit()
    logging.info(f'(Thread {thread_nr+1}) broke outside while loop (finished)')

"""
Efficiently accesses websites included in 'websites' list by using 'threadAmt' amount of threads.
Also saves every occurring https request per website in a dictionary, which the function then returns.
"""
def multiScan(websites, threadAmt, init_dir):

    manager = multiprocessing.Manager()
    q = manager.Queue()
    result = manager.dict()

    for website in websites:
        q.put(website)
    for i in range(0, threadAmt):
        q.put(None)

    threads = list()
    for i in range(0, threadAmt):

        process = multiprocessing.Process(target=scanWebsites, args=(result, q, i, init_dir))
        process.start()
        threads.append(process)

    while q.qsize() > threadAmt:
        logging.info('not empty')
        time.sleep(60)
    logging.info('queue empty')

    for process in threads:
        process.terminate()
        process.join(60)
        process.kill()

    return dict(result)