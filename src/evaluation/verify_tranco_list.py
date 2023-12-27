import requests
from zipfile import ZipFile
import os

LIST_ID = "Y52KG"
DOWNLOAD_URL = f'https://tranco-list.eu/download_daily/{LIST_ID}'

r = requests.get(DOWNLOAD_URL, allow_redirects=True)
open(f'tranco_{LIST_ID}-1m.csv.zip', 'wb').write(r.content)
with ZipFile(f'tranco_{LIST_ID}-1m.csv.zip', 'r') as zipObj:
    zipObj.extractall(path='./')

websites = []
with open('./top-1m.csv') as file:
    lines = file.readlines()
    websites = lines

websites2 = []
with open('../../resources/top-1m.csv') as file:
    lines = file.readlines()
    websites2 = lines

interrupt = False
for i in range(0, len(websites)):
    if websites[i] != websites2[i]:
        print(websites[i])
        print(websites2[i])
        interrupt = True
        break
if not interrupt:
    print("all good")
else:
    print("not good")

os.remove("./top-1m.csv")
os.remove(f'tranco_{LIST_ID}-1m.csv.zip')