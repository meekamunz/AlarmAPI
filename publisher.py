import uuid
from functions import wait, clear
from apiAccess import put, post
from time import sleep
import datetime
from json import JSONEncoder

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

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
    put(ipAddress, 'publishers', data)
    return data

def setAlarm(ipAddress, origin):
    # get time, limit to milliseconds
    t = datetime.datetime.now()
    time = t.isoformat(timespec='milliseconds')
    # override origin for testing, use same as postman
    origin = '123abcde-aabb-5678-1234-a1b2c3100001'
    data = [{'id': {'name': 'script_alarm', 'path': 'gv-emea-services/test_device'},'origin': origin, 'state': {'state': 'ok', 'timestamp': str(time)+'Z', 'value': 'testing'}}]
    jsonData = DateTimeEncoder().encode(data)
    p = post(ipAddress, 'alarms', jsonData)
    print(p)
    print(jsonData)
    wait()