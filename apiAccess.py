import requests

def get(ipAddress, call):
    # api interaction with 'call' specifying api endpoint
    getRequest = requests.get('http://' + ipAddress + ':9099/alarmapi/v1/' + call)
    return getRequest

def put(ipAddress, call, payload):
    h = {'Content-type': 'application/json', 'Accept': '*/*'}
    # api interaction with 'call' specifying api endpoint
    publish = requests.put('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload, headers=h)
    return publish

def post(ipAddress, call, payload):
    h = {'Content-type': 'application/json', 'Accept': '*/*'}
    # api interaction with 'call' specifying api endpoint
    publish = requests.post('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload, headers=h)
    return publish