def loadWebsites():
    with open('./resources/tranco_X5XLN.csv') as file:
        lines = file.readlines()
        return lines[20:]

def get(website):
    return website.split(",")[1]