import os
import json
import email.utils
import datetime

DIRECTORY = '/ba_dataset/900001-1000000/999001-1000000/'

last_date = None
last_domain = None
files = os.listdir('../../results'+DIRECTORY)
for filename in files:
    if filename.endswith('.json'):
        with open('../../results'+DIRECTORY+filename) as f:
            data = list(json.load(f))
            for entry in data:
                if not 'response' in entry:
                    continue
                response = entry['response']
                if type(response) == str:
                    response = json.loads(response)
                headers = response['headers']
                if type(headers) == str:
                    headers = json.loads(headers)
                date = None
                if 'Date' in headers:
                    date = email.utils.parsedate_to_datetime(headers['Date'])
                elif 'date' in headers:
                    date = email.utils.parsedate_to_datetime(headers['date'])
                else:
                    continue
                if last_date is None or date > last_date:
                    request = entry['request']
                    try:
                        request = data[2]['request']
                    except:
                        pass
                    if type(request) == str:
                        request = json.loads(request)
                    domain = request['url']
                    if domain == 'https://dazpin.com/':
                        continue
                    last_domain = domain
                    last_date = date
print(last_date)
print(last_domain)