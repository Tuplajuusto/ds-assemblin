from flask import Flask
from flask import make_response
from flask import request
from flask_httpauth import HTTPBasicAuth
import json

auth = HTTPBasicAuth()
app = Flask(__name__)
setpoint = 18.0
temperature = 10.0
solar = 0.0


@app.route('/assemblin/users/login/', methods=["POST"])
@auth.login_required
def login():
    print("login")
    print(request.data)

    resp = make_response("response")
    resp.set_cookie('token', 'yoyo')
    return resp

@auth.verify_password
def verify_pw(username, password):
    print(username)
    print(password)

    if (username == "digis" and password == "1234"):
        return True
    
    return False


@app.route('/assemblin/points/readablebyid/')
def readablebyid():
    print("readablebyid")
    return """[
        "Room Temperature",
        "Room Setpoint",
        "Heating Demand",
        "Cooling Demand",
        "Heating/Cooling External Control",
        "Current Outside Temperature",
        "Outside Temperature External",
        "Current Solar Power",
        "Solar Power External"
        ]"""



@app.route('/assemblin/points/writeablebyid')
def writablebyid():
    print("writablebyid")
    return """[
        "Room Setpoint",
        "Heating Demand",
        "Cooling Demand",
        "Heating/Cooling External Control",
        "Outside Temperature External",
        "Solar Power External"
        ]"""



@app.route('/assemblin/users/refresh')
def refresh():
    print("refresh")
    return "ok"


@app.route('/assemblin/points/writebyid', methods=["PUT"])
def writebyid():
    print("writebyid")

    data = request.json

    for i in range(len(data)):
        if (data[i]["id"] == "Room Setpoint"):
            global setpoint
            setpoint = float(data[i]["value"])
    
    for i in range(len(data)):
        if (data[i]["id"] == "Outside Temperature External"):
            global temperature
            temperature = float(data[i]["value"])

    for i in range(len(data)):
        if (data[i]["id"] == "Solar Power External"):
            global solar
            solar = float(data[i]["value"])


    return """[{"id":"Room Setpoint", "value": "21"}] """


@app.route('/assemblin/points/byid', methods=["POST"])
def byid():
    print("byid")
    return """
    [{"id": "Room Temperature", "value": "21.654724"}, 
    {"id": "Room Setpoint", "value": """ + "\"" + str(setpoint) + "\"" + """}, 
    {"id": "Heating Demand", "value": "0.000000"}, 
    {"id": "Heating Power", "value": "0.000000"}, 
    {"id": "Cooling Demand", "value": "30.157513"}, 
    {"id": "Cooling Power", "value": "30.157513"}, 
    {"id": "Current Outside Temperature", "value": """ + "\"" + str(temperature) + "\"" + """}, 
    {"id": "Current Solar Power", "value": """ + "\"" + str(solar) + "\"" + """ },
    {"id": "Supply Air Temp", "value": "18.558475"}]"""


@app.route('/assemblin/trends/values', methods=["POST"])
def trends_values():
    print("trends_values")
    return """
    [{"name": "HEATING POWER", "values": [{"time": "2020-12-16T13:57:00+02:00", "value": "0"}, 
    {"time": "2020-12-16T13:58:00+02:00", "value": "0"}, {"time": "2020-12-16T13:59:00+02:00", "value": "0"}]}]
    """


@app.route('/assemblin/trends', methods=["GET"])
def trends_list():
    print("trends_list")
    return """
    ['Outside Temperature', 'Outside Temp 24h avg', 'Sun Power', 'Room Temperature', 
    'Room Setpoint', 'Heating Demand', 'Cooling Demand', 'Cooling Water Supply', 
    'Heating Water Supply', 'Number of People', 'HEATING POWER', 'COOLING POWER', '301 TE10 TULOILMA']
    """


@app.route('/')
def index():
    return "hello"


if __name__ == '__main__':
    app.run(ssl_context='adhoc')
