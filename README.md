The bus_analysis project's goal is to analyze the data of the bus locations in Warsaw
using the data collected from api.um.warszawa.pl website. The analysis is split into 2 parts:

1. Scraping the data
2. Analyzing the scraped data

Both source files are in './bus_analysis/bus_analysis' folder.

Scraper.py

The scraper contains 4 main functions:

- get_bus_info(w_file, rng)
    The function takes 2 arguments. The first one being the write file of the data,
    and the second one being the number of tics. The buses usually change
    their geolocation output every 10 seconds. The number of tics means how many timestamps will be scraped, where every tic gets scraped each 10 seconds. Each line's format is as following:
        {
            'result': [{bus_timestamp}, ...],
            'Date': 'YYYY-MM-DD HH:00:00'
        }
    Where bus_timestamp's format is:
        {
            "Lines": (str)
            "Lon": (float)
            "VehicleNumber": (str)
            "Time": (str)
            "Lat": (float)
            "Brigade": (str)
        }
    Each bus has its' own VehicleNumber.
    The Line and Brigade determine the schedule that the bus follows on that specific day. 


- get_busstop_info(w_file)
    The function takes 1 argument being the write file of the data. It writes a json to the file having the form of:
        {
            'result': [
                {"values": [
                    {key: "zespol", value: (str)},
                    {key: "slupek", value: (str)},
                    {key: "nazwa_zespolu", value: (str)},
                    {key: "id_ulicy", value: (str)},
                    {key: "szer_geo", value: (str)},
                    {key: "dlug_geo", value: (str)},
                    {key: "kierunek", value: (str)},
                    {key: "obowiazuje_od", value: (str)}
                ]},
                ...
            ]
            'Date': 'YYYY-MM-DD HH:00:00'
        }
    Where the keys meanings are:
        - zespol - id of the busstop
        - slupek - id of the pole. Each busstop may have few poles on different sides of the street etc.
        - nazwa_zespolu - The name od the busstop
        - szer_geo - Latitude of the busstop being a parsed float
        - dlug_geo - Longitude of the busstop being a parsed float
        - kierunek - Direction that the busstop is facing
        - obowiazuje_od - Date since when the busstop is in operation

- get_busstop_loc_info(busstop_file, w_file)
    The function takes 2 arguments, first being the name of file being read from, 
    the second one being the name of file being written to. 
    The first file must be of the same format as the file written from get_busstop_info() function. 
    The function takes the information from the read file, 
    and puts into the w_file the information of this format:
    {
        "BusstopId/PoleId" : [Lat, Lon] ([str, str]), 
        ...
    }

- get_bus_schedule(busstop_file, w_file)
    The function takes 2 arguments, first beeing analogical to the get_busstop_loc_info function, the second one being the file being written to. The function takes each busstop from the first file, and requests an information from the api about the lines passing through the stop, and the schedules of the buslines. Then, the function arranges the data and writes it to the w_file in given format: 
    {
        "Line/Brigade": [
            ["Time", "PoleId", "BusstopId"],
            ...
        ]
    }
    This lets us easily access the schedule of certain line and brigade, which becomes useful while conducting the analysis



Analyze.py

The analyze.py file contains 2 main analysing functions:
- get_speeding_info(businfo_file, csv_line, csv_loc, vis_file):
    businfo_file - name ofread file of format returned by get_bus_info()
    csv_line - name of .csv file which will contain the lines that were speeding the most frequently
    csv_loc - name of .csv file which will contain the locations where buses were speeding the most frequently, 
        each being a square of length 111m x 111m
    vis_file - name of .html file which will contain the visualization of speeding buses. 
        It displays a map of warsaw containing trails of 4 different colours. 
        Red displaying speed of over 80km/h, orange - >=70km/h, yellow - >=60km/h, green - >=50km/h

    The function analyses the businfo_file line by line, and computes the time_delta and distance driven by each vehicle.
    Then it calculates speed based on speed and distance.

- get_lateness_info(businfo_file,
                    busschedule_file,
                    busstoploc_file,
                    csv_line,
                    csv_bstop,
                    vis_file):

    businfo_file - name of read file of format returned by get_bus_info()
    busschedule_file - name of read file of format returned by get_bus_schedule()
    busstoploc_file - name of read file of format returned by get_busstop_loc_info()
    csv_line - name of .csv file which will contain the lines that were being late the most frequently
    csv_bstop - name of .csv file which will contain the busstops that had buses late the most frequently
    vis_file - name of .html file which will contain the visualization file. 
        Each busstop gets marked by a dot. Red meaning lateness of over 20 minutes, orange - 10 mins, yellow - 5 mins, green - 3 mins

    Firstly, each bus must be identified by their VehicleNumber, Line and Brigade. 
    For each bus the function calculates the current following busstop that the bus is comming to.
    It searches the busschedule of bus' line and brigade, and finds the busstop, where the scheduled time
    is more than 5 minutes later than the first bus' registered time. I made an assumption that no bus can be
    on the busstop earlier than 5 minutes before its' scheduled arrival time. 

    Each time the bus reaches its' destination, the next position in the schedule becomes its' new destination