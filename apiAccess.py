import requests

def get(ipAddress, call):
    # api interaction with 'call' specifying api endpoint
    getRequest = requests.get('http://' + ipAddress + ':9099/alarmapi/v1/' + call)
    return getRequest

def put(ipAddress, call, payload):
    h = {'Content-type': 'application/json', 'Accept': '*/*'}
    # api interaction with 'call' specifying api endpoint
    putRequest = requests.put('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload, headers=h)
    return putRequest

def post(ipAddress, call, payload):
    h = {'Content-type': 'application/json', 'Accept': '*/*'}
    # api interaction with 'call' specifying api endpoint
    postRequest = requests.post('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload, headers=h)
    return postRequest

def delete(ipAddress, call, payload):
    h = {'Content-type': 'application/json', 'Accept': '*/*'}
    if payload != None:
        deleteRequest = requests.delete('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload, headers=h)
    else:
        deleteRequest = requests.delete('http://' + ipAddress + ':9099/alarmapi/v1/' + call, headers=h)
    return deleteRequest