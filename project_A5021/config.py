###
###  Contains all constants for configuration:
###  settings.ini
###
###  Fallbacks are essentially default values.
###
from configparser import ConfigParser
import os

# settings
REST_CATEGORY = "REST"
REST_URL = "url"
REST_URL_FALLBACK = "127.0.0.1"
REST_PORT = "port"
REST_PORT_FALLBACK = "5000"
REST_USERNAME = "username"
REST_USERNAME_FALLBACK = "digis"
REST_PASSWORD = "password"
REST_PASSWORD_FALLBACK = "1234"
REST_SSL_VERIFY = "SSL_cert_verify"
REST_SSL_VERIFY_FALLBACK = "False"

FMI_CATEGORY = "FMI"
FMI_STOREDQUERY_ID = "storedquery_id"
FMI_STOREDQUERY_ID_FALLBACK = "fmi::forecast::harmonie::surface::point::multipointcoverage"
FMI_PLACE = "place"
FMI_PLACE_FALLBACK = "kumpula,helsinki"
FMI_STARTTIME = "starttime"
FMI_STARTTIME_FALLBACK = None

GENERAL_CATEGORY = "GENERAL"
GENERAL_SAVE_TEMPERATURES = "save_temperatures"
GENERAL_SAVE_TEMPERATURES_FALLBACK = "True"
GENERAL_SAVE_TEMPERATURES_FILENAME = "save_temperatures_file"
GENERAL_SAVE_TEMPERATURES_FILENAME_FALLBACK = "temperatures.csv"
GENERAL_OUTPUT_FILENAME = "output_filename"
GENERAL_OUTPUT_FILENAME_FALLBACK = "output_data.csv"
GENERAL_TIME_HORIZON = "time_horizon"
GENERAL_TIME_HORIZON_FALLBACK = "4"
GENERAL_TRENDS = "save_trends"
GENERAL_TRENDS_FALLBACK = "HEATING POWER,COOLING POWER"
GENERAL_SETPOINT_MINIMUM = "setpoint_minimum"
GENERAL_SETPOINT_MINIMUM_FALLBACK = "15.0"
GENERAL_SETPOINT_MAXIMUM = "setpoint_maximum"
GENERAL_SETPOINT_MAXIMUM_FALLBACK = "25.0"
GENERAL_HEATING_CONTROL_ALLOWED = "heating_control_allowed"
GENERAL_HEATING_CONTROL_ALLOWED_FALLBACK = "True"
GENERAL_HEATING_CONTROL_HOURS = "heating_control_hours"
GENERAL_HEATING_CONTROL_HOURS_FALLBACK = "21-7"
GENERAL_HEATING_OFF_AT_HOUR = "heating_off_at_hour"
GENERAL_HEATING_OFF_AT_HOUR_FALLBACK = "21"

TIMINGS_CATEGORY = "TIMINGS"
TIMINGS_READ_REST_CYCLE = "data_read_cycle"
TIMINGS_READ_REST_CYCLE_FALLBACK = "1"
TIMINGS_READ_REST_OFFSET = "data_read_offset"
TIMINGS_READ_REST_OFFSET_FALLBACK = "30"
TIMINGS_READ_FMI_CYCLE = "FMI_read_cycle"
TIMINGS_READ_FMI_CYCLE_FALLBACK = "60"
TIMINGS_READ_FMI_OFFSET = "FMI_read_offset"
TIMINGS_READ_FMI_OFFSET_FALLBACK = "0"
TIMINGS_WRITE_DATA_CYCLE = "data_write_cycle"
TIMINGS_WRITE_DATA_CYCLE_FALLBACK = "10"
TIMINGS_WRITE_DATA_OFFSET = "data_write_offset"
TIMINGS_WRITE_DATA_OFFSET_FALLBACK = "10"
TIMINGS_WRITE_SETPOINT_CYCLE = "setpoint_write_cycle"
TIMINGS_WRITE_SETPOINT_CYCLE_FALLBACK = "1"
TIMINGS_WRITE_SETPOINT_OFFSET = "setpoint_write_offset"
TIMINGS_WRITE_SETPOINT_OFFSET_FALLBACK= "20"

INPUT_CATEGORY = "INPUT"
INPUT_SOLAR_ILMANET_FILENAME = "solar_ilmanet_filename"
INPUT_SOLAR_ILMANET_FILENAME_FALLBACK = "solar_data.csv"
INPUT_SOLAR_ILMANET_AUTODETECT = "solar_ilmanet_autodetect"
INPUT_SOLAR_ILMANET_AUTODETECT_FALLBACK = "True"
INPUT_SOLAR_FILENAME = "solar_filename"
INPUT_SOLAR_FILENAME_FALLBACK = "temperatures.csv"
INPUT_SOLAR_FROM_FILE = "solar_from_file"
INPUT_SOLAR_FROM_FILE_FALLBACK = "False"
INPUT_SOLAR_IGNORE_DATES = "solar_ignore_dates"
INPUT_SOLAR_IGNORE_DATES_FALLBACK = "False"
INPUT_SOLAR_DATE_COLUMN_INDEX = "solar_file_date_column_index"
INPUT_SOLAR_DATE_COLUMN_INDEX_FALLBACK = "0"
INPUT_SOLAR_TIME_COLUMN_INDEX = "solar_file_time_column_index"
INPUT_SOLAR_TIME_COLUMN_INDEX_FALLBACK = "2"
INPUT_SOLAR_DATA_COLUMN_INDEX = "solar_file_data_column_index"
INPUT_SOLAR_DATA_COLUMN_INDEX_FALLBACK = "3"
INPUT_TEMP_FILENAME = "temperatures_filename"
INPUT_TEMP_FILENAME_FALLBACK = "temperatures.csv"
INPUT_TEMP_FROM_FILE = "temperatures_from_file"
INPUT_TEMP_FROM_FILE_FALLBACK = "False"
INPUT_TEMP_IGNORE_DATES = "temperatures_ignore_dates"
INPUT_TEMP_IGNORE_DATES_FALLBACK = "False"
INPUT_TEMP_DATE_COLUMN_INDEX = "temperatures_file_date_column_index"
INPUT_TEMP_DATE_COLUMN_INDEX_FALLBACK = "0"
INPUT_TEMP_TIME_COLUMN_INDEX = "temperatures_file_time_column_index"
INPUT_TEMP_TIME_COLUMN_INDEX_FALLBACK = "2"
INPUT_TEMP_DATA_COLUMN_INDEX = "temperatures_file_data_column_index"
INPUT_TEMP_DATA_COLUMN_INDEX_FALLBACK = "4"



config = ConfigParser(allow_no_value=True)
config_file = os.path.join(os.path.dirname(__file__), "settings.ini")

# load file if it exists,
# or create a new settings file with default values
if os.path.isfile(config_file):
    config.read(os.path.join(os.path.dirname(__file__), "settings.ini"))
else:
    config.add_section(REST_CATEGORY)
    config.set(REST_CATEGORY, REST_URL, REST_URL_FALLBACK)
    config.set(REST_CATEGORY, REST_PORT, REST_PORT_FALLBACK)
    config.set(REST_CATEGORY, REST_USERNAME, REST_USERNAME_FALLBACK)
    config.set(REST_CATEGORY, "# string formatting rules apply to passwords")
    config.set(REST_CATEGORY, REST_PASSWORD, REST_PASSWORD_FALLBACK)
    config.set(REST_CATEGORY, REST_SSL_VERIFY, REST_SSL_VERIFY_FALLBACK)

    config.add_section(FMI_CATEGORY)
    config.set(FMI_CATEGORY, "# stored query from FMI open data, starttime and place parameters are added to this")
    config.set(FMI_CATEGORY, FMI_STOREDQUERY_ID, FMI_STOREDQUERY_ID_FALLBACK)
    config.set(FMI_CATEGORY, FMI_PLACE, FMI_PLACE_FALLBACK)
    config.set(FMI_CATEGORY, "# if not set, will use current time as start")
    config.set(FMI_CATEGORY, "#     format: 2020-11-06T12:00:00Z")
    config.set(FMI_CATEGORY, FMI_STARTTIME, FMI_STARTTIME_FALLBACK)
    
    config.add_section(GENERAL_CATEGORY)
    config.set(GENERAL_CATEGORY, "# saves temperature and solar data to file")
    config.set(GENERAL_CATEGORY, "#    only works when data is read from FMI")
    config.set(GENERAL_CATEGORY, GENERAL_SAVE_TEMPERATURES, GENERAL_SAVE_TEMPERATURES_FALLBACK)
    config.set(GENERAL_CATEGORY, GENERAL_SAVE_TEMPERATURES_FILENAME, GENERAL_SAVE_TEMPERATURES_FILENAME_FALLBACK)
    config.set(GENERAL_CATEGORY, "# general output file")
    config.set(GENERAL_CATEGORY, GENERAL_OUTPUT_FILENAME, GENERAL_OUTPUT_FILENAME_FALLBACK)
    config.set(GENERAL_CATEGORY, "# time horizon parameter for algorithms, if needed")
    config.set(GENERAL_CATEGORY, GENERAL_TIME_HORIZON, GENERAL_TIME_HORIZON_FALLBACK)
    config.set(GENERAL_CATEGORY, "# each trend saved to trends_<trend name>.csv")
    config.set(GENERAL_CATEGORY, "#    needs minimum 5 mins runtime")
    config.set(GENERAL_CATEGORY, "#    can be left empty")
    config.set(GENERAL_CATEGORY, "#    from start to stop/exit command")
    config.set(GENERAL_CATEGORY, GENERAL_TRENDS, GENERAL_TRENDS_FALLBACK)
    config.set(GENERAL_CATEGORY, "# the minimum and maximum setpoints, overwrite any values that are out of range")
    config.set(GENERAL_CATEGORY, GENERAL_SETPOINT_MINIMUM, GENERAL_SETPOINT_MINIMUM_FALLBACK)
    config.set(GENERAL_CATEGORY, GENERAL_SETPOINT_MAXIMUM, GENERAL_SETPOINT_MAXIMUM_FALLBACK)
    config.set(GENERAL_CATEGORY, "# allows manual heating control")
    config.set(GENERAL_CATEGORY, GENERAL_HEATING_CONTROL_ALLOWED, GENERAL_HEATING_CONTROL_ALLOWED_FALLBACK)
    config.set(GENERAL_CATEGORY, "# hours during which heating control can be adjusted")
    config.set(GENERAL_CATEGORY, GENERAL_HEATING_CONTROL_HOURS, GENERAL_HEATING_CONTROL_HOURS_FALLBACK)
    config.set(GENERAL_CATEGORY, "# heating (and cooling) will be turned off at the start of this hour")
    config.set(GENERAL_CATEGORY, "# use non hour number to deactivate this feature, example -1")
    config.set(GENERAL_CATEGORY, GENERAL_HEATING_OFF_AT_HOUR, GENERAL_HEATING_OFF_AT_HOUR_FALLBACK)


    config.add_section(TIMINGS_CATEGORY)
    config.set(TIMINGS_CATEGORY, "# cycle length in minutes")
    config.set(TIMINGS_CATEGORY, "#    calculation starts from the beginning of the current hour")
    config.set(TIMINGS_CATEGORY, TIMINGS_READ_FMI_CYCLE, TIMINGS_READ_FMI_CYCLE_FALLBACK)
    config.set(TIMINGS_CATEGORY, TIMINGS_READ_REST_CYCLE, TIMINGS_READ_REST_CYCLE_FALLBACK)
    config.set(TIMINGS_CATEGORY, TIMINGS_WRITE_DATA_CYCLE, TIMINGS_WRITE_DATA_CYCLE_FALLBACK)
    config.set(TIMINGS_CATEGORY, TIMINGS_WRITE_SETPOINT_CYCLE, TIMINGS_WRITE_SETPOINT_CYCLE_FALLBACK)
    config.set(TIMINGS_CATEGORY, "# offsets in seconds")
    config.set(TIMINGS_CATEGORY, "#    e.g. reading data happens at 30 seconds past by default (hh:mm:30)")
    config.set(TIMINGS_CATEGORY, "#    if processes happen on the same minute, offsets state the order")
    config.set(TIMINGS_CATEGORY, TIMINGS_READ_FMI_OFFSET, TIMINGS_READ_FMI_OFFSET_FALLBACK)
    config.set(TIMINGS_CATEGORY, TIMINGS_READ_REST_OFFSET, TIMINGS_READ_REST_OFFSET_FALLBACK)
    config.set(TIMINGS_CATEGORY, TIMINGS_WRITE_DATA_OFFSET, TIMINGS_WRITE_DATA_OFFSET_FALLBACK)
    config.set(TIMINGS_CATEGORY, TIMINGS_WRITE_SETPOINT_OFFSET, TIMINGS_WRITE_SETPOINT_OFFSET_FALLBACK)

    config.add_section(INPUT_CATEGORY)
    config.set(INPUT_CATEGORY, INPUT_SOLAR_ILMANET_FILENAME, INPUT_SOLAR_ILMANET_FILENAME_FALLBACK)
    config.set(INPUT_CATEGORY, "# if set to true, tries to load the newest solar_export*.csv file")
    config.set(INPUT_CATEGORY, "#    if a file is found it's prioritized over the above file")
    config.set(INPUT_CATEGORY, INPUT_SOLAR_ILMANET_AUTODETECT, INPUT_SOLAR_ILMANET_AUTODETECT_FALLBACK)
    config.set(INPUT_CATEGORY, "# filename for non-Ilmanet solar data")
    config.set(INPUT_CATEGORY, INPUT_SOLAR_FILENAME, INPUT_SOLAR_FILENAME_FALLBACK)
    config.set(INPUT_CATEGORY, "# if true, the above file will be used to load solar data")
    config.set(INPUT_CATEGORY, INPUT_SOLAR_FROM_FILE, INPUT_SOLAR_FROM_FILE_FALLBACK)
    config.set(INPUT_CATEGORY, "# if true, dates will be ignore and only first 24h values used")
    config.set(INPUT_CATEGORY, "#    essentially a testing mode")
    config.set(INPUT_CATEGORY, INPUT_SOLAR_IGNORE_DATES, INPUT_SOLAR_IGNORE_DATES_FALLBACK)
    config.set(INPUT_CATEGORY, "# column indexes, count starting at 0")
    config.set(INPUT_CATEGORY, "#    default values are set to match the file where temperature values are saved,")
    config.set(INPUT_CATEGORY, "#    which is defined in general settings")
    config.set(INPUT_CATEGORY, INPUT_SOLAR_DATE_COLUMN_INDEX, INPUT_SOLAR_DATE_COLUMN_INDEX_FALLBACK)
    config.set(INPUT_CATEGORY, INPUT_SOLAR_TIME_COLUMN_INDEX, INPUT_SOLAR_TIME_COLUMN_INDEX_FALLBACK)
    config.set(INPUT_CATEGORY, INPUT_SOLAR_DATA_COLUMN_INDEX, INPUT_SOLAR_DATA_COLUMN_INDEX_FALLBACK)
    config.set(INPUT_CATEGORY, "# filename for loading temperature data directly from a file")
    config.set(INPUT_CATEGORY, INPUT_TEMP_FILENAME, INPUT_TEMP_FILENAME_FALLBACK)
    config.set(INPUT_CATEGORY, "# if true, the above file will be used to load temperature data")
    config.set(INPUT_CATEGORY, INPUT_TEMP_FROM_FILE, INPUT_TEMP_FROM_FILE_FALLBACK)
    config.set(INPUT_CATEGORY, "# same as with solar")
    config.set(INPUT_CATEGORY, INPUT_TEMP_IGNORE_DATES, INPUT_TEMP_IGNORE_DATES_FALLBACK)
    config.set(INPUT_CATEGORY, INPUT_TEMP_DATE_COLUMN_INDEX, INPUT_TEMP_DATE_COLUMN_INDEX_FALLBACK)
    config.set(INPUT_CATEGORY, INPUT_TEMP_TIME_COLUMN_INDEX, INPUT_TEMP_TIME_COLUMN_INDEX_FALLBACK)
    config.set(INPUT_CATEGORY, INPUT_TEMP_DATA_COLUMN_INDEX, INPUT_TEMP_DATA_COLUMN_INDEX_FALLBACK)


    with open(config_file, "w") as output_file:
        config.write(output_file)
