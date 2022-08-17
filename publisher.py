import uuid
from functions import wait, clear
from apiAccess import put, post
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
    data = {'name': name, 'origin': origin}
    p = put(ipAddress, 'publishers', data)
    print('Maintaining alarms for Publisher: '+name+', PublisherID: '+origin)
    print('Press \'<ctrl+c>\' to stop')
    i=0
    try:
        while True:
            if p.status_code == 201:
                p
                print(i, p)
                i=i+10
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