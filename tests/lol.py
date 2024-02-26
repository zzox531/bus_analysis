import json
from datetime import datetime, timedelta
import folium
import os
import pandas as pd
from math import cos, asin, sqrt, pi


def check_data(el):
    assert datetime.strptime(el['Time'], '%Y-%m-%d %H:%M:%S')
    assert float(el['Lat']) >= -90
    assert float(el['Lat']) <= 90
    assert float(el['Lon']) >= -90
    assert float(el['Lon']) <= 90


def convert_t(time_str):
    # Convert str time to datetime
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')


def calc_distance(lat1, lon1, lat2, lon2):
    # Calculate distance between two lat&lon points
    r = 6371  # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a)) * 1000


def str_to_dt(time_str):
    # Convert time str to datetime, considering unusual times
    # such as 25:40:00 will be converted to 1 day 01:40:00
    hours, minutes, seconds = map(int, time_str.split(':'))
    overflow_days = hours // 24
    remainder_hours = hours % 24
    adjusted_time_str = f"{remainder_hours:02d}:{minutes:02d}:{seconds:02d}"
    time_parsed = datetime.strptime(adjusted_time_str, "%H:%M:%S")
    final_datetime = time_parsed + timedelta(days=overflow_days)

    return final_datetime


def df_inc_col2(df, val_1, col_1, col_2):
    # Increment column 2 in dataframe having val_1 as col_1
    mask = (df[col_1] == val_1)
    if df[mask].empty:
        new_row = pd.DataFrame({col_1: [val_1], col_2: [1]})
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        index = df.loc[mask].index[0]
        df.at[index, col_2] += 1
    return df


def df_inc_col3(df, val_1, val_2, col_1, col_2, col_3):
    # Increment column 3 in dataframe having val_1 as col_1 and val_2 as col_2
    mask = (df[col_1] == val_1) & (df[col_2] == val_2)
    if df[mask].empty:
        new_row = pd.DataFrame({col_1: [val_1], col_2: [val_2], col_3: [1]})
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # Increment Times_exceeded if the pair exists
        index = df.loc[mask].index[0]
        df.at[index, col_3] += 1
    return df


def file_to_dict(filename):
    # Open and load a file to json
    with open(filename, 'r') as file:
        return json.loads(file.read())


def set_bus_info(lst, bus_info):
    # Set bus_info for every element of list
    for el in lst:
        check_data(el)
        bus_info[el['VehicleNumber']] = el
        bus_info[el['VehicleNumber']] = el


def get_speeding_color(speed):
    if (speed > 22.222):  # speed in (80; 90] km/h
        return 'red'
    elif (speed > 19.444):  # speed in (70; 80] km/h
        return 'orange'
    elif (speed > 16.667):  # speed in (60; 70] km/h
        return 'yellow'
    return 'green'  # speed in (50; 60] km/h


def write_speeding_results(
        exceeding_loc,
        exceeding_lines,
        speeding_map,
        csv_line,
        csv_loc,
        vis_file):
    dir = os.getcwd() + '/analyzed_data'
    os.makedirs(dir, exist_ok=True)
    exceeding_loc = exceeding_loc.sort_values(by='Times_exceeded', ascending=False)
    exceeding_lines = exceeding_lines.sort_values(by='Times_exceeded', ascending=False)
    csv_line = './analyzed_data/' + csv_line
    csv_loc = './analyzed_data/' + csv_loc
    vis_file = './analyzed_data/' + vis_file
    exceeding_loc.to_csv(csv_loc, index=False)
    exceeding_lines.to_csv(csv_line, index=False)
    speeding_map.save(vis_file)


def get_speeding_info(businfo_file, csv_line, csv_loc, vis_file):
    # Analyze businfo data, and write speeding
    # result to csv_line, csv_loc and vis_file
    # csv_line has info on speeding of certain lines
    # csv_loc has info on speeding in certain locations
    # vis_file is a visualization html file map
    businfo_file = './scraped_data/' + businfo_file
    timestamps = 0
    incorrect_timestamps = 0
    over_the_limit = 0
    cur_dct = {}

    speeding_map = folium.Map(
        location=(52.22967823126715, 21.012233109266305),
        zoom_start=12,
        tiles="cartodb positron"
    )

    exceeding_lines = pd.DataFrame({
        'Line': pd.Series(dtype='string'),
        'Times_exceeded': pd.Series(dtype='int'),
    })

    exceeding_loc = pd.DataFrame({
        'Lat': pd.Series(dtype='float'),
        'Lon': pd.Series(dtype='float'),
        'Times_exceeded': pd.Series(dtype='float'),
    })

    bus_info = {}
    with open(businfo_file, 'r') as file:
        # Set the first timetamp as beginning location
        set_bus_info(json.loads(file.readline())['result'], bus_info)
        cur_tstamp = file.readline()
        # Iterate through all file lines
        while cur_tstamp:
            cur_dct = json.loads(cur_tstamp)['result']
            # Iterate through every timestamp of current line
            for el in cur_dct:
                cur_vehicle = el['VehicleNumber']
                cur_line = el['Lines']
                if (cur_vehicle not in bus_info):
                    bus_info[cur_vehicle] = el
                    continue
                timestamps += 1
                cur_bus = bus_info[cur_vehicle]
                cur_lat = float(cur_bus['Lat'])
                cur_lon = float(cur_bus['Lon'])
                prev_lat = float(el['Lat'])
                prev_lon = float(el['Lon'])
                coords_1 = (cur_lat, cur_lon)
                time_1 = convert_t(cur_bus['Time'])
                coords_2 = (el['Lat'], el['Lon'])
                time_2 = convert_t(el['Time'])
                time_spent = (time_2 - time_1)
                seconds = time_spent.seconds
                dist = calc_distance(cur_lat, cur_lon, prev_lat, prev_lon)
                if (seconds != 0 and dist / seconds > 25 or  # > 90km/h
                        seconds == 0 and coords_1 != coords_2 or
                        time_spent.days < 0):  # time_1 > time_2
                    incorrect_timestamps += 1
                elif (seconds != 0 and
                        dist / seconds > 13.888):  # > 50km/h
                    r_lat = round(cur_lat, 3)
                    r_lon = round(cur_lon, 3)
                    exceeding_lines = df_inc_col2(
                        exceeding_lines,  # DataFrame
                        cur_line,  # val_1
                        'Line',  # col_1
                        'Times_exceeded'  # col_2
                    )
                    exceeding_loc = df_inc_col3(
                        exceeding_loc,  # DataFrame
                        r_lat,  # val_1
                        r_lon,  # val_2
                        'Lat',  # col_1
                        'Lon',  # col_2
                        'Times_exceeded'  # col_3
                    )
                    trail = [coords_1, coords_2]
                    folium.PolyLine(
                        locations=trail,
                        color=get_speeding_color(dist / seconds),
                        weight=3,
                        tooltip=cur_vehicle
                    ).add_to(speeding_map)
                    over_the_limit += 1
                bus_info[cur_vehicle] = el
            cur_tstamp = file.readline()
    write_speeding_results(
        exceeding_loc,
        exceeding_lines,
        speeding_map,
        csv_line,
        csv_loc,
        vis_file
    )
    res = {
        'timestamps': timestamps,
        'incorrect_timestamps': incorrect_timestamps,
        'over_the_limit': over_the_limit,
    }
    return res


# While analyzing the bus punctuality, I made an assumption, that no bus can
# arrive at the busstop 5 minutes earlier before the actual time on its' route.
# This makes the program not analyze the first 5 minutes of busstop locations


def delta_t(t1, t2):
    # Return difference between two datetimes (as str)
    delta = str_to_dt(t1) - str_to_dt(t2)
    return delta


# This function finds the index of the first scheduled stop for given line,
# brigade and bus_time such that the time difference between bus_time and time
# in the schedule is at least 5 min. For example, for time 15:24:30,
# the time of returned scheduled stop must be >= 15:29:30


def find_cur_stop(busschedule, line, brigade, bus_time):
    # Find current stop that the bus is heading to
    try:
        res = next(
            i for i, v in enumerate(busschedule[line + '/' + brigade])
            if delta_t(v[0], bus_time[11:]) >= timedelta(minutes=5)
        )
        return res
    except StopIteration:
        return -1


def get_late_color(delta):
    if (delta > timedelta(minutes=20)):
        return 'red'
    elif (delta > timedelta(minutes=10)):
        return 'orange'
    elif (delta > timedelta(minutes=5)):
        return 'yellow'
    return 'green'


def write_lateness_results(
        late_lines,
        late_bstops,
        buses_late,
        csv_line,
        csv_bstop,
        vis_file):
    buses_late_map = folium.Map(
        location=(52.22967823126715, 21.012233109266305),
        zoom_start=12,
        tiles="cartodb positron"
    )
    buses_late.sort(key=lambda x: x['Delay'])
    for el in buses_late:
        msg = el['VLB']
        cords = el['Location']
        cords[0] = float(cords[0])
        cords[1] = float(cords[1])
        folium.PolyLine(
            locations=[cords, cords],
            color=get_late_color(el['Delay']),
            weight=4,
            tooltip=msg
        ).add_to(buses_late_map)
    dir = os.getcwd() + '/analyzed_data'
    os.makedirs(dir, exist_ok=True)
    late_lines = late_lines.sort_values(by='Times_late', ascending=False)
    late_bstops = late_bstops.sort_values(by='Times_late', ascending=False)
    csv_line = './analyzed_data/' + csv_line
    csv_bstop = './analyzed_data/' + csv_bstop
    vis_file = './analyzed_data/' + vis_file
    late_lines.to_csv(csv_line, index=False)
    late_bstops.to_csv(csv_bstop, index=False)
    buses_late_map.save(vis_file)


def buses_on_time(businfo_file,
                  busschedule_file,
                  busstoploc_file,
                  csv_line,
                  csv_bstop,
                  vis_file):
    # Analyze businfo data, and write lateness
    # result to csv_line, csv_bstop and vis_file
    # csv_line has info on lateness of certain lines
    # csv_bstop has info on lateness in certain locations
    # vis_file is a visualization html file map
    businfo_file = './scraped_data/' + businfo_file
    busschedule_file = './scraped_data/' + busschedule_file
    busstoploc_file = './scraped_data/' + busstoploc_file
    busschedule = file_to_dict(busschedule_file)
    busstoploc = file_to_dict(busstoploc_file)
    cur_stops = {}
    buses_late = []
    # Create map centered on Warsaw
    late_lines = pd.DataFrame({
        'Line': pd.Series(dtype='string'),
        'Times_late': pd.Series(dtype='int'),
    })
    late_bstops = pd.DataFrame({
        'BstopId': pd.Series(dtype='string'),
        'BstopNr': pd.Series(dtype='string'),
        'Times_late': pd.Series(dtype='int'),
    })
    timestamps = 0
    incorrect_timestamps = 0
    with open(businfo_file, 'r') as file:
        cur_tstamp = file.readline()
        while cur_tstamp:
            cur_dct = json.loads(cur_tstamp)
            for el in cur_dct['result']:
                check_data(el)
                if (convert_t(el['Time']) < convert_t(cur_dct['Date'])):
                    continue
                cur_vehicle = el['VehicleNumber']
                cur_line = el['Lines']
                cur_brig = el['Brigade']
                cur_lb = cur_line + '/' + cur_brig
                cur_vlb = cur_vehicle + '/' + cur_lb
                cur_time = el['Time']
                timestamps += 1
                if (cur_lb not in busschedule):
                    incorrect_timestamps += 1
                    continue
                if (cur_vlb not in cur_stops):
                    cur_time = el['Time']
                    stop_id = find_cur_stop(
                        busschedule,
                        cur_line,
                        cur_brig,
                        cur_time
                    )
                    cur_stops[cur_vlb] = stop_id
                if (cur_stops[cur_vlb] == -1):
                    continue
                stop_id = cur_stops[cur_vlb]
                cur_stop = busschedule[cur_lb][stop_id]
                cur_stop_loc = busstoploc[cur_stop[2] + '/' + cur_stop[1]]
                cur_lat = float(el['Lat'])
                cur_lon = float(el['Lon'])
                dest_lat = float(cur_stop_loc[0])
                dest_lon = float(cur_stop_loc[1])
                cur_dist = calc_distance(cur_lat, cur_lon, dest_lat, dest_lon)
                if (cur_dist < 250):
                    time_delta = delta_t(el['Time'][11:], cur_stop[0])
                    if (str_to_dt(el['Time'][11:]) > str_to_dt(cur_stop[0]) and
                            time_delta > timedelta(minutes=3)):
                        late_lines = df_inc_col2(
                            late_lines,  # DataFrame
                            cur_line,  # val_1
                            'Line',  # col_1
                            'Times_late',  # col_2
                        )
                        late_bstops = df_inc_col3(
                            late_bstops,  # DataFrame
                            cur_stop[2],  # val_1
                            cur_stop[1],  # val_2
                            'BstopId',  # col_1
                            'BstopNr',  # col_2
                            'Times_late'  # col_3
                        )
                        buses_late.append({
                            'VLB': cur_vlb,
                            'Location': cur_stop_loc,
                            'Delay': time_delta
                        })
                    cur_stops[cur_vlb] += 1
                    if (cur_stops[cur_vlb] == len(busschedule[cur_lb])):
                        cur_stops[cur_vlb] = -1
                elif (stop_id + 1 != len(busschedule[cur_lb])):
                    next_stop = busschedule[cur_lb][stop_id + 1]
                    next_loc = busstoploc[next_stop[2] + '/' + next_stop[1]]
                    next_lat = float(next_loc[0])
                    next_lon = float(next_loc[1])
                    next_dist = calc_distance(cur_lat, cur_lon, next_lat, next_lon)
                    if (next_dist < cur_dist):
                        cur_stops[cur_vlb] += 1
            cur_tstamp = file.readline()
    write_lateness_results(
        late_lines,
        late_bstops,
        buses_late,
        csv_line,
        csv_bstop,
        vis_file
    )
    res = {
        'timestamps': timestamps,
        'incorrect_timestamps': incorrect_timestamps
    }
    return res

