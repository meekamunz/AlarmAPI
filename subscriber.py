from apiAccess import get, put
from time import sleep
import json
import threading

# createSubscriber — accepts a list of device path strings
def createSubscriber(ipAddress, devicePaths):
    devices = [{'path': p} for p in devicePaths]
    data = {'type': 'pull', 'filter': devices}
    subscriber = put(ipAddress, 'subscribers', data)
    return subscriber.content.decode("utf-8")

# getSubscriber
def getSubscriber(ipAddress, subId):
    r = get(ipAddress, 'subscribers?subscriptionId='+subId)
    if r.status_code == 200:
        return True
    else: 
        return False

# getAlarmSubs — polls for alarm changes, calls callback with data
# Uses long polling: server blocks up to 30s when no data, returns immediately when data available
def getAlarmSubs(ipAddress, subId, stop_event=None, callback=None):
    if stop_event is None:
        stop_event = threading.Event()
    try:
        while not stop_event.is_set():
            p = get(ipAddress, 'alarms/changes?subscriptionId='+subId)
            if p.status_code == 200:
                data = json.loads(p.content)
                if callback:
                    callback(data)
            elif p.status_code == 204:
                # No events during this poll cycle, continue polling
                continue
            else:
                if callback:
                    callback(None)
                break
    except Exception:
        pass

# subscribeAll
def subscribeAll(ipAddress):
    deviceList = json.loads(get(ipAddress, 'devices').text)
    devices = [{'path': d} for d in deviceList]
    data = {'type': 'pull', 'filter': devices}
    subscriber = put(ipAddress, 'subscribers', data)
    return subscriber.content.decode("utf-8")

