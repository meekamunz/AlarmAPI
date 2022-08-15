import requests

def get(ipAddress, call):
    # api interaction with 'call' specifying api endpoint
    getRequest = requests.get('http://' + ipAddress + ':9099/alarmapi/v1/' + call)
    return getRequest