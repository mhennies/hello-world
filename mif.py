import urllib.request
import re
import time

debug = 1
retry = 120  # seconds
update = 600 # seconds


def url_vz(UUID, value):
    url = 'http://demo.volkszaehler.org/middleware.php/data/'
    url = url + str(UUID) + '.json?operation=add&value=' + str(value)
    return url


while True:
    url_mif = 'http://www.mif.uni-freiburg.de/stationold/'
    try:
        response = urllib.request.urlopen(url_mif)
    except:
        if debug:
            print('Error fetching html page, retry in ' + str(retry) + ' seconds!')
        time.sleep(retry)
        continue
    data = response.read().decode('iso8859-1')  # check meta tag charset or headers
    if debug > 1:
        print(data)
    # Datum
    match = re.search(r'Datum\:\s(\d\d\.\d\d\.\d\d\d\d)', data)
    if match:
        mydate = match.group(1)
        if debug:
            print(mydate)
    # Uhrzeit
    match = re.search(r'Zeit\:\s(\d\d\:\d\d)\sUhr', data)
    if match:
        mytime = match.group(1)
        if debug:
            print(mytime)
    # Temperatur
    match = re.search(r'(\-?\d+\.\d)\s°C', data)
    if match:
        mytemp = match.group(1)
        if debug:
            print(mytemp)
        UUID = 'b6aa49c0-c517-11e7-91e8-b16c985944a3'
        response = urllib.request.urlopen(url_vz(UUID, mytemp))
    # Globalstrahlung
    match = re.search(r'(\d+)\sW/m', data)
    if match:
        radiation = match.group(1)
        if debug:
            print(radiation)
        UUID = '0202f320-c51a-11e7-9bf3-21b5b5311c13'
        response = urllib.request.urlopen(url_vz(UUID, radiation))
    # wait for next update
    time.sleep(update)
