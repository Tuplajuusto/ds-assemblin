###
###  Functions for acquiring temperature data:
###    get_fmi_data() - downloads data from FMI in text format
###    get_temperature_data() - uses above and then converts to a datetime - value pair list
###    get_solar_radiation(filename) - gets solar radiation data from a file in above format
###    load_temperatures_from_file(filename) - temperatures from csv file
###
###  Parameters adjustable in settings.ini
###
import requests
import xml.etree.ElementTree as ET
from config import config
import config as CONFIG
from datetime import datetime, timedelta
import logging
import csv


# If time is none, it gets data starting from current hour.
def get_fmi_data():
    storedquery_id = config.get(CONFIG.FMI_CATEGORY, CONFIG.FMI_STOREDQUERY_ID, \
                                                    fallback=CONFIG.FMI_STOREDQUERY_ID_FALLBACK)
    place = config.get(CONFIG.FMI_CATEGORY, CONFIG.FMI_PLACE, fallback=CONFIG.FMI_PLACE_FALLBACK)
    starttime = validate_time(config.get(CONFIG.FMI_CATEGORY, CONFIG.FMI_STARTTIME, \
                                                    fallback=CONFIG.FMI_STARTTIME_FALLBACK))

    logging.info("Getting data from FMI.")
    payload = {"storedquery_id": storedquery_id, "place": place, "starttime": starttime}
    r = requests.get("http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&parameters=temperature",\
                                                     params=payload)
    logging.info("   Response:" + str(r.status_code))

    return r.text


def validate_time(time: str):
    try: 
        datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
        return time
    except:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    
def get_temperature_data():
    output = []

    data = get_fmi_data()
    root = ET.fromstring(data)

    # find start time and data in xml tree
    start_datetime = datetime.strptime(root[0][0][0][0][0].text, "%Y-%m-%dT%H:%M:%SZ")
    temperature_list = root[0][0][6][0][1][0][1].text.split()

    # add dates and times
    for x in range(len(temperature_list)):
        # offset by 1h as FMI data is for the previous hour
        # e.g. 18:00 is for 17-18
        new_datetime = start_datetime + timedelta(hours=(1 * x) - 1)
        line = (new_datetime, temperature_list[x])
        output.append(line)

    return output


def get_solar_from_ilmanet(filename: str):
    output = []

    try:
        with open(filename, newline='') as solar_data:
            csv_data = csv.reader(solar_data)

            # skip first line
            next(csv_data)
            
            # get request id from second line
            request_id = None
            for row in csv_data:
                request_id = row[0]
                break

            # reset file back to start
            solar_data.seek(0)

            for row in csv_data:
                if (row[0] == request_id):
                    # timestamp and global solar radiation
                    datetime_value = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S+02")
                    # minus one hour to make values match current hours
                    datetime_value = (datetime_value + timedelta(hours=-1))
                    line = (datetime_value, row[20])
                    output.append(line)
    except Exception as e:
        logging.error("Error loading Ilmanet data from "+ filename + ": " + str(e))

    return output

# indexes are column indexes in the file.
# counting starts at 0.
def load_temperatures_from_file(filename: str, row: int, date_index: int, time_index: int, start_index: int):
    output = []

    with open(filename, "r") as data_file:
        try:
            #read line at row, remove \n and split by ','
            data = data_file.readlines()[row].splitlines()[0].split(",")
            date_time = datetime.strptime(data[date_index] + data[time_index], "%d/%m/%Y%H:%M:%S")

            for i in range(len(data) - start_index):
                _data = (date_time + timedelta(hours=i), data[i + start_index])
                output.append(_data)

        except Exception as e:
            logging.error("Loading temperatures from a file failed")
            logging.error(str(e))

    return output


def load_data_from_file(filename: str, date_index: int, time_index: int, data_index: int):
    output = []

    try:
        with open(filename, newline='') as data_file:
            csv_data = csv.reader(data_file)

            # skip first line
            next(csv_data)
            
            for row in csv_data:
                date_time = datetime.strptime(row[date_index] + row[time_index], "%d/%m/%Y%H:%M:%S")
                _output = (date_time, row[data_index])
                output.append(_output)

    except Exception as e:
        logging.error("Error loading data from "+ filename + ": " + str(e))

    return output


def replace_dates_with_today(data: list):
    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year

    output = []

    for _data in data:
        output.append((_data[0].replace(day=day, month=month, year=year), _data[1]))

    return output

