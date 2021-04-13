###
### Algorithms for calculating setpoint go here,
### into calculate_setpoint function.
###
###
from datetime import datetime, timedelta
from config import config
import config as CONFIG
import numpy as np
import joblib
import sklearn
import os
# for model zoltan
SP_pred = None

# solar_data and temperature_data are lists of datetime - value pairs
#   Use get_temperature_at and get_solar_at functions to get values,
#   e.g. get_temperature_at(temperature_data, 0) returns temperature for current hour.
# air_temp is the current air temperature read from the system.
# time_horizon is read from settings.ini
#
# return setpoint (float)
def calculate_setpoint(room_temperature: float, solar_data: list, temperature_data: list, \
                                                    time_horizon: int, air_temp: float):
    
    room_temp = float(room_temperature)
    old_setpoint = normal_setpoint()
    current_temp = get_temperature_at(temperature_data, 0)
    temp_1hour = get_temperature_at(temperature_data, 1)
    temp_2hour = get_temperature_at(temperature_data, 2)
    temp_4hour = get_temperature_at(temperature_data, 4)
    #hour = datetime.now().hour
    #minute = datetime.now().minute


    #return round(model3(room_temp, old_setpoint, current_temp, temp_1hour, temp_2hour, temp_4hour), 5)
    #return round(ML_model(room_temp,old_setpoint, current_temp, temp_1hour, temp_2hour, temp_4hour, hour, minute),5)
    return round(ML_model2(room_temp,old_setpoint, current_temp, temp_1hour, temp_2hour, temp_4hour),5)
    
    #return model_zoltan(solar_data, temperature_data, air_temp)
    #return corrected_setpoint(datetime.now().hour, datetime.now().minute)
    #return normal_setpoint()



def turn_on_heating(room_temperature: float, solar_data: list, temperature_data: list, \
                                                    time_horizon: int, air_temp: float):
    current_hour = datetime.now().hour

    if (current_hour == 3):
        return True

    return False



# helper functions, work with 24-h testing format where dates are ignored.
def get_temperature_at(temperature_data:list, offset:int):
    temperatures_ignore_dates = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_IGNORE_DATES, \
                                                fallback=CONFIG.INPUT_TEMP_IGNORE_DATES_FALLBACK)
    temperatures_from_file = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_TEMP_FROM_FILE, \
                                                fallback=CONFIG.INPUT_TEMP_FROM_FILE_FALLBACK)

    return _get_data_at(temperature_data, offset, temperatures_ignore_dates, temperatures_from_file)


def get_solar_at(solar_data:list, offset:int):
    solar_ignore_dates = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_IGNORE_DATES, \
                                                fallback=CONFIG.INPUT_SOLAR_IGNORE_DATES_FALLBACK)
    solar_from_file = config.getboolean(CONFIG.INPUT_CATEGORY, CONFIG.INPUT_SOLAR_FROM_FILE, \
                                                fallback=CONFIG.INPUT_SOLAR_FROM_FILE_FALLBACK)

    return _get_data_at(solar_data, offset, solar_ignore_dates, solar_from_file)


def _get_data_at(data:list, offset:int, ignore_dates: bool, from_file: bool):
    output = None
    now = datetime.now() + timedelta(hours=offset)

    if (data != None):
        for row in data:
            if (now.date() == row[0].date() or (ignore_dates and from_file)):
                if (now.hour == row[0].hour):
                    output = row[1]
                    break

    return float(output)

#
#
#    Algorithms:
#
#

# default (every day is treated like a weekday - could use adjustment maybe)
def normal_setpoint():
    now = datetime.now()
    if (now.hour >= 7 and now.hour < 21):
        return 21.0
    else:
        return 18


# Zoltan's model - temp_calc.py file
def model_zoltan(solar_data: list, temperature_data: list, air_temp: float):
    global SP_pred

    if SP_pred is None:
        from temp_calc import MLP_predictor
        SP_pred = MLP_predictor()

    return SP_pred._process_data(datetime.now(), air_temp, solar_data, temperature_data)


# Mai's linear regression model
def model3(room_temp, old_setpoint, current_temp, temp_1hour, temp_2hour, temp_4hour):
    now = datetime.now()
    if (now.hour >= 3 and now.hour < 7):
        weight = [0.15928377818054307,  0.882512434780585, -0.13328905314886427, 0.1868212583669926, -0.046647105257075515, -0.007336737648879483, -0.9465895872651089]
        return weight[0] * room_temp + weight[1] * old_setpoint + weight[2] * current_temp + weight[3] * temp_1hour + weight[4] * temp_2hour + weight[5] * temp_4hour + weight[6] 
    elif (now.hour >= 7 and now.hour < 21):
        return 21.0
    else:
        return 18.0


# Base for Mai's model
def corrected_setpoint(hour, minute):
    """Compute setpoint at a give time.

    Args:
        (int) hour: the current time in hour
        (int) minute: the current time in minute

    Returns:
        (float) setpoint: the new setpoint of the room

    Note: Also change the comfort range based on the new setpoint, otherwise it cannot work.
    """
    if (hour == 7 and minute > 30) or (hour == 8 and minute < 30):
        if minute < 30:
            setpoint = (minute + 30)/15 + 17
        else:
            setpoint = (minute - 30)/15 + 17
            
    elif (hour == 20 and minute > 30) or (hour == 21 and minute < 30):
        if minute < 30:
            setpoint = -(minute + 30)/15 + 21
        else:
            setpoint = -(minute - 30)/15 + 21
    
    elif hour <= 7 or hour >= 21:
        setpoint = 17
    else:
        setpoint = 21
    
    return setpoint


def ML_model(room_temp,old_setpoint, current_temp, temp_1hour, temp_2hour, temp_4hour, hour, minute):
    now = datetime.now()
    filename = joblib.load('/home/pi/Documents/ds-assemblin/project_A5020/test_model1.sav','r')
    weight = filename.coef_
    inter = filename.intercept_
    pred = inter + weight[0] * room_temp + old_setpoint * weight[1] + current_temp * weight[2] \
            + temp_1hour * weight[3] + temp_2hour * weight[4] + temp_4hour * weight[5] + hour * weight[6] + minute * weight[7]
    mse = np.square(np.subtract(room_temp,pred)).mean()
    print (mse)
    if (now.hour >= 3 and now.hour < 7):
        return (pred - mse)
    elif (now.hour >= 7 and now.hour < 21):
        return 21.0
    else:   
        return 18.0

def ML_model2(room_temp,old_setpoint, current_temp, temp_1hour, temp_2hour, temp_4hour):
    now = datetime.now()
    filename = joblib.load('/home/pi/Documents/ds-assemblin/project_A5020/test_model1.sav','r')
    weight = filename.coef_
    inter = filename.intercept_
    pred = inter + weight[0] *  old_setpoint + weight[1] * current_temp + weight[2] \
            * temp_1hour + weight[3] * temp_2hour + weight[4] * temp_4hour
    mse = np.square(np.subtract(room_temp,pred)).mean()
    print (mse)
    if (now.hour >= 3 and now.hour < 7):
        return (pred - mse)
    elif (now.hour >= 7 and now.hour < 21):
        return 21.0
    else:   
        return 18.0

