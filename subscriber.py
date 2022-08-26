from functions import wait, clear
from apiAccess import get, put
from time import sleep
import json

# createSubscriber
def createSubscriber(ipAddress):
    # multiple path entries
    numDevices = int(input('Enter the number devices do you want to monitor: '))
    devices = ['']*numDevices
    currentDeviceList = json.loads(get(ipAddress, 'devices').text)
    i=0
    deviceLoop = True
    while deviceLoop:
        if i < numDevices:
            innerLoop = True
            while innerLoop:
                testPath = input('Set device address: ')
                # check if testPath is real
                if testPath in currentDeviceList:
                    # add device to list as a json string, then close innerloop
                    devices[i] = {'path': testPath}
                    innerLoop = False
                else:
                    print('Invalid alarm address.')
                    sleep(1)
            i=i+1
        else: deviceLoop = False

    # combine device list into json data string
    data = {'type': 'pull', 'filter': devices}

    # PUT the subscriber creation
    subscriber = put(ipAddress, 'subscribers', data)
    return subscriber.content.decode("utf-8")

# getSubscriber
def getSubscriber(ipAddress, subId):
    r = get(ipAddress, 'subscribers?subscriptionId='+subId)
    if r.status_code == 200:
        return True
    else: 
        return False

# getAlarmSubs
def getAlarmSubs(ipAddress, subId):
    try:
        while True:
            p = get(ipAddress, 'alarms/changes?subscriptionId='+subId)
            if p.status_code == 200:
                data = json.loads(p.content)
                # pretty print json
                print(json.dumps(data, indent=4, sort_keys=True))
                print()
                print('Press \'<ctrl+c>\' to stop')
                sleep(0.5)
            else:
                print('Failed to get alarm updates.')
                sleep(1)
                break
    except:
        pass

# subscribeAll
def subscribeAll(ipAddress):
    # get a list of devices
    deviceList = json.loads(get(ipAddress, 'devices').text)
    
    # add json bits around device addresses
    devices = ['']*len(deviceList)
    deviceLoop = True
    i=0
    while deviceLoop:
        if i < len(devices): devices[i] = {'path': deviceList[i]}
        else: deviceLoop = False
        i=i+1
    
    # combine device list into json data string
    data = {'type': 'pull', 'filter': devices}
    
    # PUT the subscriber creation
    subscriber = put(ipAddress, 'subscribers', data)
    return subscriber.content.decode("utf-8")

