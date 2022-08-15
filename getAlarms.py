import json
from functions import wait, clear
from get import get
from time import sleep

def deviceList(ipAddress):
    # list devices, then sort
    deviceList = json.loads(get(ipAddress, 'devices').text)
    deviceList.sort()
    return deviceList

def selectDevice(ipAddress, menu):
    singleDeviceLoop = True
    while singleDeviceLoop:
        try:
            clear()
            print('List of devices:')
            print()
            devices = deviceList(ipAddress)
            #devices.sort() # removed due to sort in deviceList(ipAddress)
            deviceNum = 1
            maxDevices = len(devices)+1
            while deviceNum < maxDevices:
                deviceName = devices[deviceNum-1]
                # get all alarms for devices
                alarms = json.loads(get(ipAddress, 'alarms?path='+devices[deviceNum-1]).content)
                i=0
                # check device alarms for a user friendly name
                while i < len(alarms):
                    if alarms[i]['id']['name'] == "NAME" or alarms[i]['id']['name'] == "IDNAME":
                        deviceName = alarms[i]['state']['value']
                    i=i+1
                # create numeric list for user select
                print(' ['+str(deviceNum)+'] '+str(devices[deviceNum-1])+' - '+str(deviceName))
                deviceNum = deviceNum+1
            print(' [.]')
            print(' [0] Return to '+menu)
            # user input
            deviceSelect = int(input('Select Device number: '))
            deviceSelect = deviceSelect-1
            if 0 <= deviceSelect <= maxDevices:
                name = json.loads(get(ipAddress, 'alarms?path='+devices[deviceSelect]).content)
                # if NAME or IDNAME exists, get device name for selected device
                i=0
                while i < len(name):
                    if name[i]['id']['name'] == "NAME" or name[i]['id']['name'] == "IDNAME":
                        deviceName = name[i]['state']['value']
                    i=i+1
                device = {"address": devices[deviceSelect], "name": deviceName}
                #return device with "name" and "address" key pairs
                return device
            elif deviceSelect == -1:
                return {"address": None, "name": None}
            else:# input error handling
                print()
                print('Invalid selection.  Please use a number in the list.')
                print('Type [0] to return to '+menu)
                print()
                sleep(1)
                pass
            
        except (IndexError, ValueError) as e:# input error handling, can print(e) if required
            print()
            print('Invalid selection.  Please use a number in the list.')
            print('Type [0] to return to '+menu)
            print()
            sleep(1)
            pass

def displayAlarms(ipAddress, deviceAddress, alarmLevel):

    # set alarm state values
    failValues = ['Critical', 'Fail', 'FAIL']
    warnValues = ['Warn', 'WARN', 'Major', 'Minor']
    okValues = ['OK', 'Ok', 'ok', 'normal']
    unknownValues = ['Unknown', 'UNKNOWN', 'NoState', 'Nostate', 'nostate', 'none', 'None', 'NONE']
    allValues = failValues + warnValues + okValues + unknownValues
    if alarmLevel in failValues: state = failValues
    if alarmLevel in warnValues: state = warnValues
    if alarmLevel in okValues: state = okValues
    if alarmLevel in unknownValues: state = unknownValues
    if alarmLevel == 'all': state = allValues
    # get alarms
    results = json.loads(get(ipAddress, 'alarms?path='+deviceAddress).content)
    # for alarms matching result, append to list
    global alarms
    alarms=[]
    i=0
    while i < len(results):
        if results[i]['state']['state'] in state:
            alarms.append({'name': results[i]['id']['name'], 'path': results[i]['id']['path'], 'state': results[i]['state']['state'], 'acked': results[i]['state']['acked'], 'ackedBy': results[i]['state']['ackedBy'], 'inverted': results[i]['state']['inverted'], 'latchedState': results[i]['state']['latchedState'], 'masked': results[i]['state']['masked'], 'timestamp': results[i]['state']['timestamp'], 'unmaskedState': results[i]['state']['unmaskedState'], 'value': results[i]['state']['value']})
        i=i+1
    i=0
    while i < len(alarms):
        print('Alarm: '+alarms[i]['name'])
        print('State: '+alarms[i]['state'])
        print('Value: '+alarms[i]['value'])
        print('Timestamp: '+alarms[i]['timestamp'])
        print('------------------------------')
        i=i+1
    print('Press any key to continue')
    wait()
    return alarms