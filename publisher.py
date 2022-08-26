import uuid
from functions import wait, clear
from apiAccess import put, post, delete
from csvAlarms import importCSV
from time import sleep
import datetime

# createPublisher
def createPublisher(ipAddress):
    origin = str(uuid.uuid4())
    try:
        name = input('Enter Publisher name: ')
    except (ValueError) as e:# input error handling, can print(e) if required
            print()
            print('Invalid name')
            print()
            sleep(1)
            pass

    data = {'name': name, 'origin': origin}
    p = put(ipAddress, 'publishers', data)
    print(p)
    sleep(0.5)
    if p.status_code == 403:
        data = {'name': 'Write access on server is disabled', 'origin': None}
    return data

# maintainAlarms
def maintainAlarms(ipAddress, name, origin):
    clear()
    data = {'name': name, 'origin': origin}
    #p = put(ipAddress, 'publishers', data)
    print('Maintaining alarms for Publisher: '+name+', PublisherID: '+origin)
    print('Press \'<ctrl+c>\' to stop')
    try:
        while True:
            p = put(ipAddress, 'publishers', data)
            if p.status_code == 201:
                # publish again, then wait for 10 seconds.  
                # for some reason I can't use the 'p' variable to publish again???
                #put(ipAddress, 'publishers', data)
                sleep(10)
            else:
                print('Failed to maintain alarm publisher.')
                sleep(1)
                break
    except:
        pass

# setAlarm
def setAlarm(ipAddress, origin):
    # get time/date, limit to milliseconds
    t = datetime.datetime.now()
    time = t.isoformat(timespec='milliseconds')

    # legal state values
    states = ['unknown', 'ok', 'warn', 'fail', 'Unknown', 'Ok', 'Warn', 'Fail', 'UNKNOWN', 'OK', 'WARN', 'FAIL']

    # set custom alarm parameters
    try:
        path=input('Set device address: ')
        name=input('Set alarm name: ')
        stateLoop = True
        while stateLoop:
            state=input('Set alarm state: ')
            if state in states: stateLoop = False
            else:
                print('Invalid state.')
        value=input('Set alarm value: ')
    except (ValueError) as e:# input error handling, can print(e) if required
            print()
            print('Invalid entry.')
            print()
            sleep(1)
            pass
    data = [{'id': {'name': str(name), 'path': str(path)},'origin': str(origin), 'state': {'state': str(state), 'timestamp': str(time)+'Z', 'value': str(value)}}]
    p = post(ipAddress, 'alarms', data)
    print(p)
    if p.status_code == 409:
        print('An existing item already exists and cannot be modified.')
        wait()
    sleep(0.5)
    # return the current deviceAddress
    return path

# publishAllAlarms
def publishAllAlarms(ipAddress):
    # create publsiher
    name = 'GVO-Services'
    # need to get uuid first
    origin = str(uuid.uuid4())
    data = {'name': name, 'origin': origin}
    # Get CSV data as alarmData
    alarmData = importCSV(origin)
    # create publisher now
    pub = put(ipAddress, 'publishers', data)
    print(pub)
    # post alarm data
    p = post(ipAddress, 'alarms', alarmData)
    print(p)
    sleep(0.5)
    # maintain immediately
    maintainAlarms(ipAddress, name, origin)
    return data

# removeAlarms
def removeAlarms(ipAddress, origin):
    # set path and alarm name
    path=input('Set device address: ')
    name=input('Set alarm name: ')
    data = [{"name": name,"path": path}]
    p = post(ipAddress, 'alarms/deletions?publicationId='+origin, data)
    print(p)
    sleep(0.5)

# remove publisher
def removePublisher(ipAddress, origin):
    d = delete(ipAddress, 'publishers?publicationId='+origin, None)
    print(d)
    sleep(0.5)
    return d