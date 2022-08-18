import ipaddress
import uuid
from functions import wait, clear
from apiAccess import put, post, delete
from csvAlarms import importCSV
from time import sleep
import datetime

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
    return data

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

def setAlarm(ipAddress, origin):
    # get time, limit to milliseconds
    t = datetime.datetime.now()
    time = t.isoformat(timespec='milliseconds')

    # set custom alarm parameters
    try:
        path=input('Set device address: ')
        name=input('Set alarm name: ')
        state=input('Set alarm state: ')
        value=input('Set alarm value: ')
    except (ValueError) as e:# input error handling, can print(e) if required
            print()
            print('Invalid name')
            print()
            sleep(1)
            pass
    data = [{'id': {'name': str(name), 'path': str(path)},'origin': str(origin), 'state': {'state': str(state), 'timestamp': str(time)+'Z', 'value': str(value)}}]
    p = post(ipAddress, 'alarms', data)
    print(p)
    sleep(0.5)

def publishAllAlarms(ipAddress, origin):
    # Get CSV data as alarmData
    alarmData = importCSV(origin)
    p = post(ipAddress, 'alarms', alarmData)
    print(p)
    sleep(0.5)

def removeAlarms(ipAddress, origin):
    data = [{'id': {'name': '*'},'origin': str(origin)}]
    p = post(ipAddress, 'alarms/deletions?publicationId='+origin, data)
    print(p)
    sleep(0.5)

def removePublisher(ipAddress, origin):
    d = delete(ipAddress, 'publishers?publicationId='+origin, None)
    print(d)
    sleep(0.5)