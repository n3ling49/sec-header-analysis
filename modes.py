from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import utils
import threading
import math

WEBSITEAMT = 6
def scanWebsites(result, websites, amt = WEBSITEAMT):
    options = Options()
    options.add_argument('--headless')
    #the following two arguments somehow fix the webdriver issue in docker
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    visited = 0
    while visited < amt:
        print(websites[visited].replace("\n", ""))
        website = utils.get(websites[visited])
        driver.get('https://www.' + website)
        print("Requests: " + str(len(driver.requests)))
        result[website] = str(driver.requests)
        del driver.requests
        """
        print(driver.requests[0].headers.keys())
        for header in driver.requests[0].headers.keys():
            if header in secHeaders:
                print(header+": true")
            else:
                print(header + ": false")
        """
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