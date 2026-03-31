import uuid
from apiAccess import put, post, delete
from time import sleep
import datetime
import threading

# createPublisher
def createPublisher(ipAddress, name=None):
    origin = str(uuid.uuid4())
    if name is None:
        name = 'ROAR-Publisher'
    data = {'name': name, 'origin': origin}
    p = put(ipAddress, 'publishers', data)
    if p.status_code == 403:
        data = {'name': 'Write access on server is disabled', 'origin': None}
    return data

# maintainAlarms — runs in a loop until stop_event is set
def maintainAlarms(ipAddress, name, origin, stop_event=None, callback=None):
    if stop_event is None:
        stop_event = threading.Event()
    data = {'name': name, 'origin': origin}
    try:
        while not stop_event.is_set():
            p = put(ipAddress, 'publishers', data)
            if p.status_code == 201:
                stop_event.wait(10)
            else:
                if callback:
                    callback(False, 'Failed to maintain alarm publisher.')
                break
    except Exception:
        pass

# setAlarm
def setAlarm(ipAddress, origin, path, name, state, value):
    # get time/date, limit to milliseconds
    t = datetime.datetime.now()
    time = t.isoformat(timespec='milliseconds')

    data = [{'id': {'name': str(name), 'path': str(path)},'origin': str(origin), 'state': {'state': str(state), 'timestamp': str(time)+'Z', 'value': str(value)}}]
    p = post(ipAddress, 'alarms', data)
    return p

# publishAllAlarms — publish alarm data list, return publisher data
def publishAllAlarms(ipAddress, alarmData, name=None):
    if name is None:
        name = 'GVO-Services'
    origin = str(uuid.uuid4())
    data = {'name': name, 'origin': origin}
    # create publisher
    pub = put(ipAddress, 'publishers', data)
    # post alarm data
    p = post(ipAddress, 'alarms', alarmData)
    return {'name': name, 'origin': origin, 'pub_response': pub, 'alarm_response': p}

# removeAlarms
def removeAlarms(ipAddress, origin, path, name):
    data = [{"name": name,"path": path}]
    p = post(ipAddress, 'alarms/deletions?publicationId='+origin, data)
    return p

# remove publisher
def removePublisher(ipAddress, origin):
    d = delete(ipAddress, 'publishers?publicationId='+origin, None)
    return d
    return d