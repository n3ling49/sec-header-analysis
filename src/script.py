import utils as utils

def getfailed(data):
    keys = list(data.keys())
    failed_data = dict()

    failed = 0
    lightfailed = 0
    for key in keys:
        length = len(data[key])
        if length == 0:
            failed += 1
        if length < 3:
            lightfailed += 1
            failed_data[key] = data[key]
        
    
    print("Failed: "+str(failed))
    print("Lightfailed: "+str(lightfailed))
    print("Percentage: "+str(failed/len(keys)*100)+"%")
    print("Percentage (lightfailed): "+str(lightfailed/len(keys)*100)+"%")
    utils.save(failed_data, "failed_")

'''
with open("/app/results/2023-07-03_11:12:56_results.json") as file:
    data = json.load(file)
    getfailed(data)
'''
## liste erzeugen mit failed/lightfailed requests