import requests     # http://docs.python-requests.org/en/latest/
import re           # regex
from time import sleep, mktime, strptime, gmtime, strftime

# set verbosity of output
debug = 1

# time for next retry if MIF webserver is not reachable
retry = 120  # seconds

# update period
# identical timestamps cause error in vzlogger middleware
# => should match update frequency of MIF webserver (every 10 minutes)
update = 600 # seconds

def url_vz(UUID, value,timestamp):
    url = 'http://demo.volkszaehler.org/middleware.php/data/'
    url += str(UUID) + '.json?operation=add'
    url += '&ts=' + str(int(timestamp*1000))
    url += '&value=' + str(value)
    return url

while True:
    dataset = {}
    url_mif = 'http://www.mif.uni-freiburg.de/stationold/'
    ua ='Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    ua_header = {'user-agent': ua}

    if debug:
        print ('-='*40)
        print (strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    try:
        r = requests.get(url_mif, headers=ua_header)
    except:
        if debug:
            print('Error fetching html page, retry in ' + str(retry) + ' seconds!')
        sleep(retry)
        continue
    if r.status_code != requests.codes.ok:
        if debug:
            print ('Faulty response code: ' + str(r.status_code))
            print('Error fetching html page, retry in ' + str(retry) + ' seconds!')
        sleep(retry)
        continue
    data = r.text
    if debug > 1:
        print(data)
    # Datum
    match = re.search(r'Datum\:\s(\d\d\.\d\d\.\d\d\d\d)', data)
    if match:
        date = match.group(1)
        dataset["date"] = date
        if debug:
            print(date)
    # Uhrzeit
    match = re.search(r'Zeit\:\s(\d\d\:\d\d)\sUhr', data)
    if match:
        mtime = match.group(1)
        dataset["time"] = mtime
        if debug:
            print(mtime)
    # create timestamp (in seconds since epoche)
    timestamp = mktime(strptime(date + ' ' + mtime, '%d.%m.%Y %H:%M'))
    # Temperature
    match = re.search(r'(\-?\d+\.\d)\s°C', data)
    if match:
        temperature = match.group(1)
        dataset["temperature"] = float(temperature)
        if debug:
            print(temperature)
        UUID = 'b6aa49c0-c517-11e7-91e8-b16c985944a3'
        r = requests.get(url_vz(UUID, temperature,timestamp))
        if debug:
            if r.status_code == requests.codes.ok:
                print (r.json())
            else:
                print ('Faulty response code: ' + str(r.status_code))
    # Globalstrahlung
    match = re.search(r'(\d+)\sW/m', data)
    if match:
        radiation = match.group(1)
        dataset["radiation"] = int(radiation)
        if debug:
            print(radiation)
        UUID = '0202f320-c51a-11e7-9bf3-21b5b5311c13'
        r = requests.get(url_vz(UUID, radiation,timestamp))
        if debug:
            if r.status_code == requests.codes.ok:
                print (r.json())
            else:
                print ('Faulty response code: ' + str(r.status_code))
    # wait for next update
    if debug:
        print (dataset)
        print ('updating values in ' + str(update) +' seconds')
    sleep(update)
