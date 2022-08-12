import requests

def get(ipAddress, call):
    getRequest = requests.get('http://' + ipAddress + ':9099/alarmapi/v1/' + call)
    return getRequest