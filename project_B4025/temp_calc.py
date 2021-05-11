#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 11:17:50 2020

@author: Zoltan Gere
"""
import input_functions

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from pandas.plotting import register_matplotlib_converters

import datetime as dt
import time

register_matplotlib_converters()


class MLP_predictor:

    def __init__(self):
        self._assemblin_data = pd.DataFrame(columns=['Time', 'Airtemp'])   # datetime, airtemp
        self._reg = None
        self._setpoint_curves = pd.DataFrame()
        self._last_room_setpoint = 21.0
        self._last_time = dt.datetime.now()
        self._scaler = StandardScaler()
        self._logfile = open("ann_log.txt", "a")

        # Teach the MLP from stored dataset
        # read data from .csv
        df = pd.read_csv('training_data.csv', sep=',')
        timestamparray = []
        for i in range(df.shape[0]):
            #timestamparray.append(dt.datetime.strptime(df.iloc[i,0] + " " + df.iloc[i,1], "%d/%m/%Y %H:%M:%S").timestamp())
            d = dt.datetime.strptime(df.iloc[i,0] + " " + df.iloc[i,1], "%d/%m/%Y %H:%M:%S")
            timestamparray.append((d.hour * 3600) + (d.minute * 60) + d.second)

        # X
        td = pd.DataFrame(data=timestamparray, columns=['Time'])
        td = td.join(df.iloc[:,3:4])        # 'Room Setpoint'
        td = td.join(df.iloc[:,8:9])        # 'Current Outside Temperature'
        td = td.join(df.iloc[:,10:11])      # 'Current Solar Power'
        td = td.join(df.iloc[:,12:13])      # 'Supply Air Temp'

        self._scaler.fit(td.iloc[:,:])
        tds = pd.DataFrame(self._scaler.transform(td.iloc[:,:]))

        # Y
        td = td.join(df.iloc[:,2:3])        # 'Room Temperature'

#        print(td.describe())

        # Training data set
        X = tds.iloc[:,0:5]
        Y = td.iloc[:,5:6].squeeze()

        # # Training data set: first half
        # X = tds.iloc[0:624,0:5]
        # Y = tds.iloc[0:624,5:6].squeeze()
        # # Test data set: second half
        # X_test = tds.iloc[625:1257,0:5]
        # Y_test = tds.iloc[625:1257,5:6].squeeze()

        self._reg = MLPRegressor(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(3, 20), random_state=1, max_iter=3000)
        self._reg.fit(X,Y)


        # Y_pred = self._reg.predict(X_test)
        # mse = mean_squared_error(Y_test, Y_pred)
        # r2s = r2_score(Y_test, Y_pred)

        # print('\n\n')
        # print("MSE = ", mse)
        # print("R2s = ", r2s)
        # print("Iter = ", self._reg.n_iter_)

        # print("Pred mean:", Y_pred.mean())
#        print("Teaching finished.")

        # Make possible value list for setpoint
        curve_raise = 4
        for i in range(-20, 21):
            step = ((float(i) / 20) * curve_raise) / 240
            tr = []
            for j in range(240):
                tr.append((j+1) * step)
            td = pd.DataFrame(data = tr, columns=[i])
            if (i==-20):
                self._setpoint_curves = td
            else:
                self._setpoint_curves = self._setpoint_curves.join(td)
#        print("Curves:\n", self._setpoint_curves)

        now = dt.datetime.now()
        if (now.hour >= 8 and now.hour < 21):
            if (now.weekday() > 4):
                self._last_room_setpoint = 17
            else:
                self._last_room_setpoint = 21
        else:
            self._last_room_setpoint = 17

#        print(" Init complete.")
    # End of __init__

    # Runs once/minute
    # airtemp: single value - minutely
    # solar_data, temperature_data: list of (datetime, value) - hourly
    def _process_data(self, now: dt.datetime, airtemp: float, solar_data: list, temperature_data: list):

        # Save new assemblin data into _assemblin_data
        row = pd.DataFrame(data={'Time': [(now.hour * 3600) + (now.minute * 60) + now.second], 'Airtemp': [airtemp]})
        self._assemblin_data = self._assemblin_data.append(row)

# =============================================================================
#         # Create a copy of _assemblin_data
#         # Add solar_data and temperature_data to copy of _assemblin_data
#         X_hist = self._assemblin_data
# #        print(X_hist)
# #        print("\n\n")
#         solDat = []
#
#         for i in X_hist.iterrows():
# #            print("i:", i[1][0])
#             d = dt.datetime.fromtimestamp(i[1][0])
#             for j in solar_data:
#                 if (d.date() == j[0].date()):
#                     if (d.hour == j[0].hour):
#                         solDat.append(j[1])
# #        print("Soldat:", solDat)
# #        print("\n\n")
#         X_hist = X_hist.join(pd.DataFrame(data=solDat, columns=['Solar_data']))
#
# #        print(X_hist)
# #        print("\n\n")
#
#         tempDat = []
#         for i in X_hist.iterrows():
#             print("i:", i[1][0])
#             d = dt.datetime.fromtimestamp(i[1][0])
#             for j in temperature_data:
#                 if (d.date() == j[0].date()):
#                     if (d.hour == j[0].hour):
#                         tempDat.append(j[1])
#         X_hist = X_hist.join(pd.DataFrame(data=tempDat, columns=['Temperature_data']))
#
#         print(X_hist)
# =============================================================================

        ts_pred = []
        # Make value list for target temperature
        target_temp = pd.DataFrame(columns=['Time', 'Targettemp'])
        tt = 0
        for i in range(240):    # Prediction is 4h into the future
            dtoffs = (now + dt.timedelta(minutes=i))
            ts_pred.append(dtoffs)
            if (dtoffs.hour >= 8 and dtoffs.hour < 21):
                if (dtoffs.weekday() > 4):
                    tt = 17
                else:
                    tt = 21
            else:
                tt = 17
            row = pd.DataFrame(data={'Time': [(dtoffs.hour * 3600) + (dtoffs.minute * 60) + dtoffs.second], 'Targettemp': [tt]})
            target_temp = target_temp.append(row)
#        print("Target temp.:\n", target_temp)
#        print(target_temp.iloc[:, 1:2])

        solDat = []
        for i in ts_pred:    # Prediction is 4h into the future
            for j in solar_data:
                if (i.date() == j[0].date()):
                    if (i.hour == j[0].hour):
                        solDat.append(float(j[1]))
#        print("Solar data:\n", solDat)

        tempDat = []
        for i in ts_pred:    # Prediction is 4h into the future
            for j in temperature_data:
                if (i.date() == j[0].date()):
                    if (i.hour == j[0].hour):
                        tempDat.append(float(j[1]))
#        print("Temp data:\n", tempDat)

        sup_air = []
        for i in ts_pred:
            sup_air.append(airtemp)

        # Generate prediction dataset
        timestamparray = []
        for i in range(len(ts_pred)):
            timestamparray.append((ts_pred[i].hour * 3600) + (ts_pred[i].minute * 60) + ts_pred[i].second)
#        print("Time:\n", timestamparray)

        # X
        mses = []
        for c in range(-10, 11):
            room_sp = []
            for i in range(len(ts_pred)):
                room_sp.append(self._last_room_setpoint + (c / 2.0)-2)
            X_pred = pd.DataFrame(data=timestamparray, columns=['Time'])
            X_pred = X_pred.join(pd.DataFrame(data=room_sp, columns=['Room Setpoint']))                 # 'Room Setpoint'
#            X_pred = X_pred.join(self._setpoint_curves.iloc[:,c+20:c+21])                              # 'Room Setpoint'
            X_pred = X_pred.join(pd.DataFrame(data=tempDat, columns=['Current Outside Temperature']))   # 'Current Outside Temperature'
            X_pred = X_pred.join(pd.DataFrame(data=solDat, columns=['Current Solar Power']))            # 'Current Solar Power'
            X_pred = X_pred.join(pd.DataFrame(data=sup_air, columns=['Supply Air Temp']))               # 'Supply Air Temp'

            X_pred_scaled = pd.DataFrame(self._scaler.transform(X_pred.iloc[:,:]))

            # Make MLP make prediction
#            print(X_pred)
#            print(self._reg.predict(X_pred))
#            print(self._reg.predict(X_pred_scaled))

            try:
                Y_pred = self._reg.predict(X_pred_scaled)
                mses.append ( (c, mean_squared_error(target_temp.iloc[:, 1:2], Y_pred))  )
            except Exception as e:
                self._logfile.write(str(now))
                self._logfile.write(str(e))
                mses.append((c, 0.0))


#             if (c==-3):
#                print(X_pred.describe())
#                 print(Y_pred)
#                print(X_pred_scaled.describe())
#            print(Y_pred)
#            print("\n\n")
#            print(room_sp[0])

#        print(mses)

        # Select best scenario
        bestc = mses[0][0]
        bestmse = mses[0][1]
        for i in range(len(mses)):
            if (mses[i][1] < bestmse):
                bestc = mses[i][0]
                bestmse = mses[i][1]
#        print("Found best MSE %f at %i" % (bestmse, bestc))
        self._logfile.write(str(now))
        self._logfile.write("\tFound best MSE\t%f\t at \t%i\n" % (bestmse, bestc))

        retval = self._last_room_setpoint
        if (now.hour > self._last_time.hour or (now.hour == 0 and self._last_time.hour == 23)):
            if (bestc < -3):
                retval = self._last_room_setpoint + 0.5
            elif (bestc > 3):
                retval = self._last_room_setpoint - 0.5
            else:
                retval = self._last_room_setpoint

        self._last_room_setpoint = retval
        self._last_time = now
        self._logfile.flush()
        return(retval)

# End of class MLP_predictor



if (__name__ == '__main__'):
    

    sol_data = input_functions.get_solar_from_ilmanet("solar_data.csv")
    #print(sol_data)
    #print("\n\n")
    temp_data = input_functions.get_temperature_data()
    #print(temp_data)
    #print("\n\n")

    now_time = dt.datetime.fromisoformat('2020-12-07T23:58:10')
    now_time = dt.datetime.now()
    SP_pred = MLP_predictor()
    print("\n\n")
    print(SP_pred._process_data(now_time, 18.6, sol_data, temp_data))
    # time.sleep(1)
    print(SP_pred._process_data(now_time + dt.timedelta(minutes=1), 18.6, sol_data, temp_data))
    # time.sleep(1)
    print(SP_pred._process_data(now_time + dt.timedelta(minutes=2), 18.6, sol_data, temp_data))
    # time.sleep(1)
    print(SP_pred._process_data(now_time + dt.timedelta(minutes=3), 18.6, sol_data, temp_data))
    # time.sleep(1)
    print(SP_pred._process_data(now_time + dt.timedelta(minutes=4), 18.6, sol_data, temp_data))

