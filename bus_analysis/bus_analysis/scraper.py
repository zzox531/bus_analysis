import requests
import time
import json
import os
from datetime import datetime

apikey = '8f67b42c-27b3-44f6-8e04-7137aa1f0a9a'

urls = {
    'bus_loc': 'https://api.um.warszawa.pl/api/action/busestrams_get',
    'bus_stops': 'https://api.um.warszawa.pl/api/action/dbstore_get',
    'bus_stop_lines': 'https://api.um.warszawa.pl/api/action/dbtimetable_get',
    'bus_line_schedule': 'https://api.um.warszawa.pl/api/action/dbtimetable_get',
}


def make_scraped_dir():
    dir = os.getcwd() + '/scraped_data'
    os.makedirs(dir, exist_ok=True)


def get_response(url, params):
    date = datetime.now()
    response = requests.get(url, params)
    while (response.status_code != 200 or
            response.json()['result'] == 'Błędna metoda lub parametry wywołania'):
        date = datetime.now()
        response = requests.get(url, params)
    response_json = response.json()
    date = date.replace(minute=0, second=0, microsecond=0)
    response_json['Date'] = str(date)
    return response_json


def get_info(w_file, url, params, rng):
    make_scraped_dir()
    w_file = './scraped_data/' + w_file
    with open(w_file, 'w') as file:
        for i in range(rng):
            response_json = get_response(url, params)
            file.write(json.dumps(response_json) + '\n')
            if (rng != 1):
                time.sleep(10)


def get_bus_info(w_file, rng):
    params = {
        'resource_id': 'f2e5503e-927d-4ad3-9500-4ab9e55deb59',
        'apikey': apikey,
        'type': 1
    }
    get_info(w_file, urls['bus_loc'], params, rng)


def get_busstop_info(w_file):
    params = {
        'id': 'ab75c33d-3a26-4342-b36a-6e5fef0a3ac3',
        'sortBy': 'id',
        'apikey': apikey,
    }
    get_info(w_file, urls['bus_stops'], params, 1)


def get_busstop_loc_info(busstop_file, w_file):
    bloc_info = {}
    make_scraped_dir()
    w_file = './scraped_data/' + w_file
    busstop_file = './scraped_data/' + busstop_file
    with open(busstop_file, 'r') as file:
        bstop_info = json.loads(file.readline())['result']
    for el in bstop_info:
        busstopId = el['values'][0]['value'] + '/' + el['values'][1]['value']
        lat = el['values'][4]['value']
        lon = el['values'][5]['value']
        bloc_info[busstopId] = (lat, lon)
    with open(w_file, 'w') as file:
        file.write(json.dumps(bloc_info) + '\n')


def compute_response_data(bstop_schedule,
                          busroute_schedule,
                          bstopNr,
                          bstopId):
    for line in bstop_schedule:
        cur_line = line['values'][0]['value']
        params = {
            'id': 'e923fa0e-d96c-43f9-ae6e-60518c9f3238',
            'busstopId': bstopId,
            'busstopNr': bstopNr,
            'line': cur_line,
            'apikey': apikey
        }
        response_json = get_response(urls['bus_line_schedule'], params)
        for el in response_json['result']:
            cur_brig = el['values'][2]['value']
            arr_time = el['values'][5]['value']
            cur_lb = cur_line + '/' + cur_brig
            if (cur_lb in busroute_schedule):
                busroute_schedule[cur_lb].append((arr_time, bstopNr, bstopId))
            else:
                busroute_schedule[cur_lb] = [(arr_time, bstopNr, bstopId)]


def get_bus_schedule(busstop_file, w_file):
    busroute_schedule = {}
    make_scraped_dir()
    busstop_file = './scraped_data/' + busstop_file
    w_file = './scraped_data/' + w_file
    with open(busstop_file, 'r') as file:
        bstop_info = json.loads(file.readline())['result']
    for el in bstop_info:
        bstopId = el['values'][0]['value']
        bstopNr = el['values'][1]['value']
        params = {
            'id': '88cd555f-6f31-43ca-9de4-66c479ad5942',
            'busstopId': bstopId,
            'busstopNr': bstopNr,
            'apikey': apikey
        }
        response_json = get_response(urls['bus_stop_lines'], params)
        compute_response_data(
            response_json['result'],
            busroute_schedule,
            bstopNr,
            bstopId
        )

    for el in busroute_schedule:
        busroute_schedule[el].sort(key=lambda x: x[0])

    with open(w_file, 'w') as file:
        file.write(json.dumps(busroute_schedule) + '\n')
