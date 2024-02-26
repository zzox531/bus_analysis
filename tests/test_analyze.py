from bus_analysis import analyze
from datetime import datetime
import pytest
import json

with open('./scraped_data/busschedule.txt', 'r') as file:
    busschedule = json.loads(file.readline())    

def test_wrong_date():
    with pytest.raises(ValueError):
        analyze.get_speeding_info('wrong_date.txt', 'blank.csv', 'blank.csv', 'blank.html')


def test_wrong_coords():
    with pytest.raises(AssertionError):
        analyze.get_speeding_info('wrong_coords.txt', 'blank.csv', 'blank2.csv', 'blank.html')


def test_teleporting_bus():
    assert analyze.get_speeding_info(
        'teleporting_bus.txt',
        'blank.csv',
        'blank2.csv',
        'blank.html'
    )['incorrect_timestamps'] == 1


def test_non_existant_linebrig():
    assert analyze.get_lateness_info(
        'nonexistant_linebrig.txt',
        'busschedule.txt',
        'busstoploc.txt',
        'blank.csv',
        'blank2.csv',
        'blank.html'
    )['incorrect_timestamps'] == 1


@pytest.mark.parametrize("line, brigade, time, expected", [
    ['102', '587', '2024-02-24 4:35:00', 5],
    ['102', '587', '2024-02-24 5:46:00', 51], 
    ['102', '587', '2024-02-24 8:12:00', 135], 
    ['102', '587', '2024-02-24 23:59:00', -1],
    ['102', '587', '2024-02-24 20:34:00', 331]
])
def test_find_cur_stop(line, brigade, time, expected):
    assert analyze.find_cur_stop(busschedule, line, brigade, time) == expected


@pytest.mark.parametrize("time_str, expected", [
    ['23:40:10', datetime.strptime('1900-01-01 23:40:10', '%Y-%m-%d %H:%M:%S')],
    ['05:40:15', datetime.strptime('1900-01-01 05:40:15', '%Y-%m-%d %H:%M:%S')],
    ['25:40:10', datetime.strptime('1900-01-02 01:40:10', '%Y-%m-%d %H:%M:%S')],
    ['38:20:10', datetime.strptime('1900-01-02 14:20:10', '%Y-%m-%d %H:%M:%S')],
])
def test_str_to_dt(time_str, expected):
    assert analyze.str_to_dt(time_str) == expected
