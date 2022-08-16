import json
from functions import wait, clear
from apiAccess import get
from time import sleep

def deviceList(ipAddress):
    # list devices, then sort
    deviceList = json.loads(get(ipAddress, 'devices').text)
    deviceList.sort()
    return deviceList

def getDeviceName(dAddress, ipAddress):
    if dAddress in deviceList(ipAddress):
        # get all alarms for dAddress
        name = json.loads(get(ipAddress, 'alarms?path='+dAddress).content)
        # if NAME or IDNAME exists, get device name for selected device
        deviceName=dAddress
        i=0
        while i < len(name):
            if name[i]['id']['name'] == "NAME":
                deviceName = name[i]['state']['value']
            # I don't think I ever want to use IDNAME
            #elif name[i]['id']['name'] == "IDNAME":
            #    deviceName = name[i]['state']['value']
            i=i+1
        return deviceName

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
                # get all alarms for devices, then get name if it exists
                deviceName = getDeviceName(devices[deviceNum-1], ipAddress)
                # create numeric list for user select
                print(' ['+str(deviceNum)+'] '+str(devices[deviceNum-1])+' - '+str(deviceName))
                deviceNum = deviceNum+1
            print(' [.]')
            print(' [0] Return to '+menu)
            # user input
            deviceSelect = int(input('Select Device number: '))
            deviceSelect = deviceSelect-1
            if 0 <= deviceSelect <= maxDevices:
                deviceName = getDeviceName(devices[deviceSelect], ipAddress)
                #return device with "name" and "address" key pairs
                device = {"address": devices[deviceSelect], "name": deviceName}
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
    # handle multiple devices
    global alarms
    alarms=[]
    j=0
    while j < len(deviceAddress):
        # set alarm state values
        failValues = ['Critical', 'critical', 'Fail', 'FAIL', 'fail']
        warnValues = ['Warn', 'warn', 'WARN', 'Major', 'Minor', 'major', 'minor']
        okValues = ['OK', 'Ok', 'ok', 'normal']
        unknownValues = ['Unknown', 'UNKNOWN', 'NoState', 'Nostate', 'nostate', 'none', 'None', 'NONE']
        allValues = failValues + warnValues + okValues + unknownValues
        if alarmLevel in failValues: state = failValues
        if alarmLevel in warnValues: state = warnValues
        if alarmLevel in okValues: state = okValues
        if alarmLevel in unknownValues: state = unknownValues
        if alarmLevel == 'all': state = allValues
        # get alarms
        results = json.loads(get(ipAddress, 'alarms?path='+str(deviceAddress[j])).content)
        print('Getting '+alarmLevel+' alarms from '+str(deviceAddress[j])+'...')
        # for alarms matching result, append to list
        i=0
        while i < len(results):
            if results[i]['state']['state'] in state:
                alarms.append({'name': results[i]['id']['name'], 'path': results[i]['id']['path'], 'state': results[i]['state']['state'], 'acked': results[i]['state']['acked'], 'ackedBy': results[i]['state']['ackedBy'], 'inverted': results[i]['state']['inverted'], 'latchedState': results[i]['state']['latchedState'], 'masked': results[i]['state']['masked'], 'timestamp': results[i]['state']['timestamp'], 'unmaskedState': results[i]['state']['unmaskedState'], 'value': results[i]['state']['value']})
            i=i+1
        j=j+1
    print('Press any key to continue')
    wait()
    return alarms