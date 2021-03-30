###
### Core module for Digi-Salama Assemblin project.
### 
###
from client import Client
from datetime import datetime, timedelta
from config import config # configparser
import config as CONFIG # access to globals
from glob import glob
import input_functions
import json
import csv
import time
import threading
import os
import logging
from algorithms import calculate_setpoint, turn_on_heating

ROOM_SETPOINT = "B4023 Room Setpoint Remote"
ROOM_TEMPERATURE = "B4023 Room Temperature"
SOLAR_POWER = "Solar Power External"
OUTSIDE_TEMPERATURE = "Outside Temperature External"
AIR_TEMPERATURE = "B4023 Room Temperature"

# Core class used to start and control subprocesses:
#   - reading data from FMI
#   - writing temp/solar to REST
#   - reading data from REST
#   - writing setpoint to REST
# Each subprocess runs in its own thread parallel to others.
class Core:
    def __init__(self):
        self._solar_data = None
        self._temperature_data = None
        self._client = Client()
        self._starttime = None
        self._endtime = None
        self._reading_REST = read_REST(self._client, self)
        self._reading_FMI = read_FMI(self)
        self._writing_setpoint = write_setpoint(self._client, self)
        self._writing_data = write_data(self._client, self)
        self._save_temperatures = config.getboolean(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_SAVE_TEMPERATURES, \
                                                    fallback=CONFIG.GENERAL_SAVE_TEMPERATURES_FALLBACK)
        self._save_temperatures_filename = config.get(CONFIG.GENERAL_CATEGORY, \
                                                    CONFIG.GENERAL_SAVE_TEMPERATURES_FILENAME, \
                                                    fallback=CONFIG.GENERAL_SAVE_TEMPERATURES_FILENAME_FALLBACK)

    def stop(self):
        self._reading_REST.stop()
        self._reading_FMI.stop()
        self._writing_setpoint.stop()
        self._writing_data.stop()
        trends = config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_TRENDS, \
                                                    fallback=CONFIG.GENERAL_TRENDS_FALLBACK)
        self._endtime = datetime.now()

        # only retrieve trends if the program has ran at least 5 minutes, else might end up with a timeout error.
        if ((self._endtime - self._starttime).total_seconds() > 300 and len(trends) > 0):
            trends = trends.split(",")
            self._save_trends(trends)

    # Retrieves trends from REST and saves each into its own file
    def _save_trends(self, trends : list):
        logging.info("Saving trends: " + str(trends))
        try:
            trend_data = json.loads(self._client.trends_values(self._starttime, self._endtime, trends))
            for trend in trend_data:
                filename = "trends_" + trend['name'] + ".csv"
                with open(filename, "w") as trend_file:
                    for value in trend['values']:
                        trend_file.write(value['time'] + "," + str(value['value']) + "\n")
        except Exception as e:
            logging.error("Saving trends error")
            logging.error(str(e))
            

    def set_temperatures(self, temperature_data):
        self._temperature_data = temperature_data
        if self._save_temperatures:
            logging.info("Saving temperatures to: " + self._save_temperatures_filename)
            save_temperatures_to_file(self._solar_data, self._temperature_data, self._save_temperatures_filename)

    def get_temperatures(self):
        return self._temperature_data

    def set_solar(self, solar_data):
        self._solar_data = solar_data

    def get_solar(self):
        return self._solar_data

    def start(self):
        # not needed for now.. 
        #self._client.login()

        #
        #   Loading parameters for solar data.
        #
        solar_from_file = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_FROM_FILE, \
                                                    fallback=CONFIG.INPUT_SOLAR_FROM_FILE_FALLBACK)
        solar_ilmanet_autodetect = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_ILMANET_AUTODETECT, \
                                                    fallback=CONFIG.INPUT_SOLAR_ILMANET_AUTODETECT_FALLBACK)
    
        # from a non-Ilmanet datafile
        if solar_from_file:
            filename = config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_FILENAME, \
                                                    fallback=CONFIG.INPUT_SOLAR_FILENAME_FALLBACK)
            date_index = int(config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_DATE_COLUMN_INDEX, \
                                                    fallback=CONFIG.INPUT_SOLAR_DATE_COLUMN_INDEX_FALLBACK))
            time_index = int(config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_TIME_COLUMN_INDEX, \
                                                    fallback=CONFIG.INPUT_SOLAR_TIME_COLUMN_INDEX_FALLBACK))
            data_index = int(config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_DATA_COLUMN_INDEX, \
                                                    fallback=CONFIG.INPUT_SOLAR_DATA_COLUMN_INDEX_FALLBACK))
            logging.info("Reading solar data from file: " + filename + " date index: " + str(date_index) + \
                                                    " time index: " + str(time_index) + " data index: " + \
                                                    str(data_index))
            self._solar_data = input_functions.load_data_from_file(filename, date_index, time_index, data_index)
        # Ilmanet
        else:
            filename = config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_ILMANET_FILENAME, \
                                                    fallback=CONFIG.INPUT_SOLAR_ILMANET_FILENAME_FALLBACK)
            if solar_ilmanet_autodetect:
                try:
                    # try to find the newest export_solar... file in the folder
                    filename = max(glob("export_solar*.csv"), key = os.path.getmtime)
                    logging.info("Autodetecting Ilmanet data file: " + filename)
                except:
                    logging.info("Failed to autodetect Ilmanet datafile.")
            logging.info("Reading Ilmanet solar data from file: " + filename)
            self._solar_data = input_functions.get_solar_from_ilmanet(filename)

        solar_ignore_dates = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_IGNORE_DATES, \
                                                    fallback=CONFIG.INPUT_SOLAR_IGNORE_DATES_FALLBACK)
        if solar_ignore_dates:
            logging.info("Ignoring dates on solar data")
            self._solar_data = input_functions.replace_dates_with_today(self._solar_data)

        #
        #   Loading parameters for temperature data.
        #
        temperatures_from_file = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_FROM_FILE, \
                                                    fallback=CONFIG.INPUT_TEMP_FROM_FILE_FALLBACK)
        # datafile
        if temperatures_from_file:
            filename = config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_FILENAME, \
                                                    fallback=CONFIG.INPUT_TEMP_FILENAME_FALLBACK)
            date_index = int(config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_DATE_COLUMN_INDEX, \
                                                    fallback=CONFIG.INPUT_TEMP_DATE_COLUMN_INDEX_FALLBACK))
            time_index = int(config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_TIME_COLUMN_INDEX, \
                                                    fallback=CONFIG.INPUT_TEMP_TIME_COLUMN_INDEX_FALLBACK))
            data_index = int(config.get(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_DATA_COLUMN_INDEX, \
                                                    fallback=CONFIG.INPUT_TEMP_DATA_COLUMN_INDEX_FALLBACK))
            logging.info("Reading temperatures from file: " + filename + " date index: " + str(date_index) + \
                                                    " time index: " + str(time_index) + " data index: " + \
                                                    str(data_index))
            self._temperature_data = input_functions.load_data_from_file(filename, date_index, time_index, data_index)

            temperature_ignore_dates = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_IGNORE_DATES, \
                                                    fallback=CONFIG.INPUT_TEMP_IGNORE_DATES_FALLBACK)
            if temperature_ignore_dates:
                logging.info("Ignoring dates on temperature data")
                self._temperature_data = input_functions.replace_dates_with_today(self._temperature_data)
        else:
            # FMI
            self._temperature_data = input_functions.get_temperature_data()
            if self._save_temperatures:
                logging.info("Saving temperatures to: " + self._save_temperatures_filename)
                save_temperatures_to_file(self._solar_data, self._temperature_data, self._save_temperatures_filename)
            # start FMI reading subprocess
            self._reading_FMI.start()

        # start other subprocesses
        self._reading_REST.start()
        self._writing_setpoint.start()
        #self._writing_data.start()
        self._starttime = datetime.now()

# process for reading data from REST
class read_REST:
    def __init__(self, client: Client, core: Core):
        self._exit = False
        self._client = client
        self._core = core

    def stop(self):
        self._exit = True

    def start(self):
        self._exit = False
        thread = threading.Thread(target=self._start)
        thread.daemon = True
        thread.start()
        
    def _start(self):
        cycle_length = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_READ_REST_CYCLE, \
                                                    fallback=CONFIG.TIMINGS_READ_REST_CYCLE_FALLBACK))
        offset = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_READ_REST_OFFSET, \
                                                    fallback=CONFIG.TIMINGS_READ_REST_OFFSET_FALLBACK))
        process_time = calculate_start_time(cycle_length, offset)

        logging.info("Reading data started - Cycle length: " + str(cycle_length) + " min")

        while True:
            try:
                process_time = delay_process(process_time, cycle_length)

                # Exit here blocks the process from continuing after exit command has been given,
                # but trends are still being retrieved.
                if self._exit:
                    break

                filename = config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_OUTPUT_FILENAME, \
                                            fallback=CONFIG.GENERAL_OUTPUT_FILENAME_FALLBACK)

                logging.info("Reading data from system...")
                data = self._client.byid_all()
                write_output(filename, data)
                logging.info("   Reading data complete")

            except Exception as e:
                logging.error("Reading data error")
                logging.error(str(e))

# process for getting data from FMI
class read_FMI:
    def __init__(self, core: Core):
        self._exit = False
        self._core = core

    def stop(self):
        self._exit = True

    def start(self):
        self._exit = False
        thread = threading.Thread(target=self._start)
        thread.daemon = True
        thread.start()

    def _start(self):
        cycle_length = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_READ_FMI_CYCLE, \
                                                    fallback=CONFIG.TIMINGS_READ_FMI_CYCLE_FALLBACK))
        offset = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_READ_FMI_OFFSET, \
                                                    fallback=CONFIG.TIMINGS_READ_FMI_OFFSET_FALLBACK))
        process_time = calculate_start_time(cycle_length, offset)

        logging.info("Reading FMI temperature data started - Cycle length: " + str(cycle_length) + " min")

        while True:
            try:
                process_time = delay_process(process_time, cycle_length)

                if self._exit:
                    break

                logging.info("Getting FMI temperature data...")
                temperature_data = input_functions.get_temperature_data()
                self._core.set_temperatures(temperature_data)
                logging.info("   Getting FMI temperature data complete")

            except Exception as e:
                logging.error("Getting FMI temperature data error")
                logging.error(str(e))


# process for writing data to REST
class write_data:
    def __init__(self, client: Client, core: Core):
        self._exit = False
        self._client = client
        self._core = core

    def stop(self):
        self._exit = True

    def start(self):
        self._exit = False
        thread = threading.Thread(target=self._start)
        thread.daemon = True
        thread.start()

    def _start(self):
        cycle_length = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_WRITE_DATA_CYCLE, \
                                                    fallback=CONFIG.TIMINGS_WRITE_DATA_CYCLE_FALLBACK))
        offset = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_WRITE_DATA_OFFSET, \
                                                    fallback=CONFIG.TIMINGS_WRITE_DATA_OFFSET_FALLBACK))
        process_time = calculate_start_time(cycle_length, offset)

        solar_ignore_dates = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_IGNORE_DATES, \
                                                    fallback=CONFIG.INPUT_SOLAR_IGNORE_DATES_FALLBACK)
        solar_from_file = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_FROM_FILE, \
                                                    fallback=CONFIG.INPUT_SOLAR_FROM_FILE_FALLBACK)

        temperatures_ignore_dates = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_IGNORE_DATES, \
                                                    fallback=CONFIG.INPUT_TEMP_IGNORE_DATES_FALLBACK)
        temperatures_from_file = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_FROM_FILE, \
                                                    fallback=CONFIG.INPUT_TEMP_FROM_FILE_FALLBACK)
      
        logging.info("Writing temperature and solar started - Cycle length: " + str(cycle_length) + " min")

        while True:
            try:
                process_time = delay_process(process_time, cycle_length)

                if self._exit:
                    break

                solar_data = self._core.get_solar()
                temperature_data = self._core.get_temperatures()

                logging.info("Writing temperature and solar data to system...")
                self._process_data(solar_data, temperature_data, temperatures_ignore_dates, temperatures_from_file, \
                                                    solar_ignore_dates, solar_from_file)
                logging.info("   Writing temperature and solar data complete")

            except Exception as e:
                logging.error("Writing temperature and solar data error")
                logging.error(str(e))

    # writing function
    def _process_data(self, solar_data: list, temperature_data: list, temperatures_ignore_dates: bool, \
                                                    temperatures_from_file: bool, solar_ignore_dates: bool, \
                                                    solar_from_file: bool):
        now = datetime.now()
        data = []

        if (solar_data != None):
            for row in solar_data:
                if (now.date() == row[0].date() or (solar_ignore_dates and solar_from_file)):
                    if (now.hour == row[0].hour):
                        data.append((SOLAR_POWER, row[1]))
                        break
        
        if (temperature_data != None):
            for row in temperature_data:
                if (now.date() == row[0].date() or (temperatures_ignore_dates and temperatures_from_file)):
                    if (now.hour == row[0].hour):
                        data.append((OUTSIDE_TEMPERATURE, row[1]))
                        break

        self._client.writebyid_multiple(data)

# process for writing setpoint
class write_setpoint:
    def __init__(self, client: Client, core: Core):
        self._exit = False
        self._client = client
        self._core = core

    def stop(self):
        self._exit = True

    def start(self):
        self._exit = False
        thread = threading.Thread(target=self._start)
        thread.daemon = True
        thread.start()

    def _start(self):
        time_horizon = int(config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_TIME_HORIZON, \
                                            fallback=CONFIG.GENERAL_TIME_HORIZON_FALLBACK))
        setpoint_minimum = float(config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_SETPOINT_MINIMUM, \
                                            fallback=CONFIG.GENERAL_SETPOINT_MINIMUM_FALLBACK))
        setpoint_maximum = float(config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_SETPOINT_MAXIMUM, \
                                            fallback=CONFIG.GENERAL_SETPOINT_MAXIMUM_FALLBACK))

        cycle_length = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_WRITE_SETPOINT_CYCLE, \
                                                    fallback=CONFIG.TIMINGS_WRITE_SETPOINT_CYCLE_FALLBACK))
        offset = int(config.get(CONFIG.TIMINGS_CATEGORY, CONFIG.TIMINGS_WRITE_SETPOINT_OFFSET, \
                                                    fallback=CONFIG.TIMINGS_WRITE_SETPOINT_OFFSET_FALLBACK))
        process_time = calculate_start_time(cycle_length, offset)

        logging.info("Writing setpoint started - Cycle length: " + str(cycle_length) + " min")


        heating_off_at_hour = int(config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_HEATING_OFF_AT_HOUR, \
                                                    fallback=CONFIG.GENERAL_HEATING_OFF_AT_HOUR_FALLBACK))
        heating_is_off = False

        while True:
            try:
                process_time = delay_process(process_time, cycle_length)

                if self._exit:
                    break

                solar_data = self._core.get_solar()
                temperature_data = self._core.get_temperatures()

                logging.info("Getting room and air temperature from system...")
                input_data = list()
                input_data.append(ROOM_TEMPERATURE)
                input_data.append(AIR_TEMPERATURE)

                data = json.loads(self._client.byid_multiple(input_data))

                room_temperature = float(get_value(data, ROOM_TEMPERATURE))
                air_temperature = float(get_value(data, AIR_TEMPERATURE))
                logging.info("   Temperatures retrieved, room: " + str(room_temperature) + \
                                                    " air: " + str(air_temperature))
                
                logging.info("Calculating new setpoint...")
                setpoint = calculate_setpoint(room_temperature, solar_data, temperature_data, \
                                                    time_horizon, air_temperature)
                logging.info("   Calculating new setpoint complete: " + str(setpoint))

                if (setpoint < setpoint_minimum):
                    setpoint = setpoint_minimum
                elif (setpoint > setpoint_maximum):
                    setpoint = setpoint_maximum

                output = []
                output.append((ROOM_SETPOINT, setpoint))
                output.append(("External Control", 1))

                #if ((is_heating_control_allowed() == True)):
                    #output.append(("External Control", 1))
                    #time.sleep(840)

                if (datetime.now().hour == heating_off_at_hour and heating_is_off != True \
                                                    and is_heating_control_allowed()):
                    logging.info("Turning heating/cooling external control on.")
                    output.append(("B4023 Heating Disabled", 1))
                    output.append(("B4023 Cooling Disabled", 1))
                    output.append(("External Control", 1))
                    heating_is_off = True

                if (is_heating_control_allowed() != True):
                    if (heating_is_off == True):
                        logging.info("Turning heating/control external control off - outside allowed time range")
                        heating_is_off = False
                    output.append(("B4023 Heating Disabled", 0))
                    output.append(("B4023 Cooling Disabled", 0))
                    output.append(("External Control", 0))

                if (heating_is_off and is_heating_control_allowed() and turn_on_heating( \
                                                    room_temperature, \
                                                    solar_data, \
                                                    temperature_data, \
                                                    time_horizon, \
                                                    air_temperature)):
                    logging.info("Turning heating/control external control off - manual call")
                    heating_is_off = False
                    output.append(("B4023 Heating Disabled", 0))
                    output.append(("B4023 Cooling Disabled", 1))
                    output.append(("External Control", 0))

                logging.info("Writing new setpoint to system: " + str(setpoint))
                self._client.writebyid_multiple(output)
                logging.info("   Writing new setpoint complete")

            except Exception as e:
                logging.error("Writing setpoint error")
                logging.error(str(e))


# return 'value' for target 'id' 
def get_value(data: list, target: str):
    for i in range(len(data)):
        if (data[i]["id"] == target):
            return data[i]["value"]
    
    return None


# calculates the time for first cycle minus cycle length
def calculate_start_time(offset: int, seconds: int):
    starttime = datetime.now()

    minutes = 0
    while (starttime.minute >= minutes):
        minutes += offset

    minutes -= offset
    return starttime.replace(minute=minutes, second=seconds, microsecond=0)

# sleep until next cycle
def delay_process(process_time: datetime, cycle_length: int):
    while (process_time < datetime.now()):
        process_time = process_time + timedelta(minutes=cycle_length)

    time.sleep((process_time - datetime.now()).total_seconds())
    return process_time

# saves temperature (and solar) data to a file
#   only used when FMI reading is live
def save_temperatures_to_file(solar: list, data: list, filename: str):
    _solar = "NaN"
    now = datetime.now()

    if (solar != None):
        for row in solar:
            if (now.date() == row[0].date()):
                if (now.hour == row[0].hour):
                    _solar = row[1]
                    break

    # headers
    if not (os.path.exists(filename)):
        with open(filename, "w") as data_file:
            data_file.write("Date,Record Time,0 Temp Time,Solar Radiation,0 Temp")

            for x in range(len(data) - 1):
                data_file.write(",+" + str(x + 1))
            data_file.write("\n")

    with open(filename, "a") as data_file:
        data_file.write(data[0][0].strftime("%d/%m/%Y"))        # date
        data_file.write(datetime.now().strftime(",%H:%M:%S"))   # record time
        data_file.write(data[0][0].strftime(",%H:%M:%S"))       # 0 temp time
        data_file.write(","+_solar)

        for x in data:
            data_file.write("," + x[1])
        data_file.write("\n")


def write_output(filename: str, input_data: str):
    data = json.loads(input_data)

    # headers
    if not (os.path.exists(filename)):
        with open(filename, "w") as data_file:
            data_file.write("Date,Time")
            for x in range(len(data)):
                data_file.write("," + data[x]["id"])
            data_file.write("\n")

    with open(filename, "a") as data_file:
        _datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S").split()
        data_file.write(_datetime[0] + "," + _datetime[1])
        for x in range(len(data)):
            data_file.write("," + data[x]["value"])
        data_file.write("\n")


def is_heating_control_allowed():
    time_range = config.get(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_HEATING_CONTROL_HOURS, \
                                                    fallback=CONFIG.GENERAL_HEATING_CONTROL_HOURS_FALLBACK) \
                                                    .split("-")
    heating_control_allowed = config.getboolean(CONFIG.GENERAL_CATEGORY, CONFIG.GENERAL_HEATING_CONTROL_ALLOWED, \
                                                    fallback=CONFIG.GENERAL_HEATING_CONTROL_ALLOWED_FALLBACK) 

    current_hour = datetime.now().hour
    start_hour = int(time_range[0])
    end_hour = int(time_range[1])

    if (heating_control_allowed):
        if (start_hour == end_hour):
            return True
        elif (current_hour >= start_hour and start_hour > end_hour):
            return True
        elif (current_hour < end_hour and start_hour > end_hour):
            return True
        elif (current_hour >= start_hour and current_hour < end_hour):
            return True
    else:
        return False

