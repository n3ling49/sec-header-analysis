from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import utils
import threading


WEBSITEAMT = 30
def scanWebsites(websites, amt = WEBSITEAMT):
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.add_argument('--headless')

    # initializing webdriver for Chrome with our options
    driver = webdriver.Chrome(options=options)

    visited = 0
    while visited < amt:
        print(websites[visited].replace("\n", ""))
        driver.get('https://www.' + utils.get(websites[visited]))
        print("Requests: " + str(len(driver.requests)))
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

def multiScan(websites, threads):
    #TODO: generalize
    websitesPerThread = int(WEBSITEAMT/threads)
    thread1 = threading.Thread(target=scanWebsites, args=(websites[:websitesPerThread], websitesPerThread,)) #will break if websiteamt is not dividible by threads
    thread2 = threading.Thread(target=scanWebsites, args=(websites[websitesPerThread:2*websitesPerThread], websitesPerThread,))
    thread3 = threading.Thread(target=scanWebsites, args=(websites[2*websitesPerThread:3*websitesPerThread], websitesPerThread,)) #will break if websiteamt is not dividible by threads
    thread4 = threading.Thread(target=scanWebsites, args=(websites[3*websitesPerThread:4*websitesPerThread], websitesPerThread,))
    thread5 = threading.Thread(target=scanWebsites, args=(websites[4*websitesPerThread:5*websitesPerThread], websitesPerThread,)) #will break if websiteamt is not dividible by threads
    thread6 = threading.Thread(target=scanWebsites, args=(websites[5*websitesPerThread:], websitesPerThread,))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()