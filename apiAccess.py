import requests

# Shared session for HTTP connection pooling (keep-alive)
_session = requests.Session()
_session.headers.update({'Content-type': 'application/json', 'Accept': '*/*'})

# get
def get(ipAddress, call):
    # api interaction with 'call' specifying api endpoint
    getRequest = _session.get('http://' + ipAddress + ':9099/alarmapi/v1/' + call)
    return getRequest

# put
def put(ipAddress, call, payload):
    # api interaction with 'call' specifying api endpoint
    putRequest = _session.put('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload)
    return putRequest

# post
def post(ipAddress, call, payload):
    # api interaction with 'call' specifying api endpoint
    postRequest = _session.post('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload)
    return postRequest

# delete
def delete(ipAddress, call, payload):
    if payload != None:
        deleteRequest = _session.delete('http://' + ipAddress + ':9099/alarmapi/v1/' + call, json=payload)
    else:
        deleteRequest = _session.delete('http://' + ipAddress + ':9099/alarmapi/v1/' + call)
    return deleteRequest

# purge
def purge(ipAddress):
    purge = _session.get('http://' + ipAddress + '/monitoringnode/system/purge')
    return purge