###
### Class Client handles connections to Assemblin REST API.
###
###
import requests
from config import config
import config as CONFIG
from datetime import datetime
import logging
import threading

# removes warnings for unverified connections
# comment out if causing problems
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Client:
    def __init__(self):
        self._url = config.get(CONFIG.REST_CATEGORY, CONFIG.REST_URL, fallback=CONFIG.REST_URL_FALLBACK)
        self._port = config.get(CONFIG.REST_CATEGORY, CONFIG.REST_PORT, fallback=CONFIG.REST_PORT_FALLBACK)
        self._username = config.get(CONFIG.REST_CATEGORY, CONFIG.REST_USERNAME, fallback=CONFIG.REST_USERNAME_FALLBACK)
        self._password = config.get(CONFIG.REST_CATEGORY, CONFIG.REST_PASSWORD, fallback=CONFIG.REST_PASSWORD_FALLBACK)
        self._session = requests.Session()
        self._session.verify = config.getboolean(CONFIG.REST_CATEGORY, CONFIG.REST_SSL_VERIFY, \
                                                    fallback=CONFIG.REST_SSL_VERIFY_FALLBACK)
        self._cookie = token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IiIsImFkbWluIjpmYWxzZSwiZXhwIjoxNjE2MTQ5NzEzfQ.DFhV40ZRCu_a_fRAUZYKiZPxuFxaaTqzwBMhDl_CU7o
        self._lock = threading.Lock()

    def __create_url(self, path):
        return "https://" + str(self._url) + ":" + str(self._port) + path
    

    # login is currently not really doing anything, might need adjustments if it gets fixed on the REST side.
    def login(self):
        logging.info("Login to Assemblin REST")
        r = self._session.post(self.__create_url("/assemblin/users/login"), auth=(self._username, self._password), \
                                                    timeout=5)
        logging.info("   Response:" + str(r.status_code))
        # cookies are somewhat buggy
        
        print(r.headers["Set-Cookie"])
        print(r.headers["Set-Cookie"].split('=')[1].split(';')[0])
        #self._session.cookies["token"] = r.headers["Set-Cookie"].split('=')[1].split(';')[0]
        print(self._session.cookies)
        print(self._cookie)
        
        

    # not used anywhere currently - if login is fixed, then might be worth a look
    def refresh(self):
        logging.info("Token refresh")
        r = self._session.get(self.__create_url("/assemblin/users/refresh"), timeout=5)
        logging.info("   Response:" + str(r.status_code))


    def readablebyid(self):
        logging.info("Call readablebyid")
        r = self._session.get(self.__create_url("/assemblin/points/readablebyid"), timeout=5)
        logging.info("   Response:" + str(r.status_code))
        

    def writeablebyid(self):
        logging.info("Call writeablebyid")
        r = self._session.get(self.__create_url("/assemblin/points/writeablebyid"), timeout=5)
        logging.info("   Response:" + str(r.status_code))
        

    def writebyid(self, id, value):
        with self._lock:
            _data = {}
            _data["id"] = id
            _data["value"] = str(value)
            _data2 = list()
            _data2.append(_data)
            logging.info("Call writebyid")
            logging.info("   Inputs:")
            logging.info("     id:" + id)
            logging.info("     value:" + str(value))
            r = self._session.put(self.__create_url("/assemblin/points/writebyid"), json=_data2, timeout=5)
            logging.info("   Response:" + str(r.status_code))
        

    def writebyid_multiple(self, data):
        with self._lock:
            _data2 = list()
            for i in range(len(data)):
                _data = {}
                _data["id"] = data[i][0]
                _data["value"] = str(data[i][1])
                _data2.append(_data)
            
            logging.info("Call writebyid_multiple")
            logging.info("   Inputs:")
            for row in _data2:
                logging.info("     id: " + row["id"] + "  value: " + row["value"])
            r = self._session.put(self.__create_url("/assemblin/points/writebyid"), json=_data2, timeout=5)
            logging.info("   Response:" + str(r.status_code))
        

    # byid - methods for reading data
    def byid(self, id):
        with self._lock:
            _data = list()
            _data.append(id)
            logging.info("Call byid")
            logging.info("   Input:" + id)
            r = self._session.post(self.__create_url("/assemblin/points/byid"), json=_data, timeout=5)
            logging.info("   Response:" + str(r.status_code))
            return(r.text)


    def byid_multiple(self, id_list: list):
        with self._lock:
            _data = list()
            for x in id_list:
                _data.append(x)
            logging.info("Call byid_multiple")
            logging.info("   Input: " + str(id_list))
            r = self._session.post(self.__create_url("/assemblin/points/byid"), json=_data, timeout=5)
            logging.info("   Response:" + str(r.status_code))
            return(r.text)


    # heating / cooling external control means that heating and cooling demand can be manually adjusted
    #    0 automatic, 1 manual
    # temp / solar external are used to input current temperature / solar, and change to -999 a few seconds later
    def byid_all(self):
        with self._lock:
            _data = list()
            _data.append("A5020 Room Temperature")
            _data.append("A5020 Room Setpoint Actual")
            _data.append("A5020 Heating Demand")
            _data.append("A5020 Cooling Demand")
            _data.append("A5020 Heating Disabled")
            _data.append("A5020 Cooling Disabled")
            _data.append("A5020 Room Setpoint Remote")
            _data.append("A5020 Heating Power")
            _data.append("A5020 Cooling Power")
    #        _data.append("Outside Temperature External")
    #        _data.append("Current Solar Power")
    #        _data.append("Solar Power External")
    #        _data.append("Supply Air Temp")
            logging.info("Call byid_all")
            logging.info("   Input: All")
            r = self._session.post(self.__create_url("/assemblin/points/byid"), json=_data, timeout=5)
            logging.info("   Response:" + str(r.status_code))
            return r.text

    # trends return values the simulator recorded for given period of time.
    # different inputs to byid - methods
    def trends_values(self, from_: datetime, to: datetime, points: list):
        _data = {}
        _data["from"] = from_.strftime("%d/%m/%Y %H:%M:%S")
        _data["to"] = to.strftime("%d/%m/%Y %H:%M:%S")
        _data["points"] = points

        logging.info("Call trends_values")
        logging.info("   from: " + from_.strftime("%d.%m.%Y%%20%H:%M:%S"))
        logging.info("     to: " + to.strftime("%d.%m.%Y%%20%H:%M:%S"))
        logging.info("   points:" + str(points))

        r = self._session.post(self.__create_url("/assemblin/trends/values"), json=_data)

        logging.info("   Response:" + str(r.status_code))
        return r.text

    def trends_values_all(self, from_: datetime, to: datetime):
        logging.info("Call trends_values_all")
        logging.info("   from: " + from_.strftime("%d.%m.%Y%%20%H:%M:%S"))
        logging.info("     to: " + to.strftime("%d.%m.%Y%%20%H:%M:%S"))

        payload = {'from': from_.strftime("%d.%m.%Y%%20%H:%M:%S"), 'to': to.strftime("%d.%m.%Y%%20%H:%M:%S")}
        r = self._session.get(self.__create_url("/assemblin/trends/values_all"), params=payload)
        logging.info("   Response:" + str(r.status_code))
        return r.text


    def trends_list(self):
        logging.info("Call trends_list")
        r = self._session.get(self.__create_url("/assemblin/trends"), timeout=5)
        logging.info("   Response:" + str(r.status_code))
        return r.text


