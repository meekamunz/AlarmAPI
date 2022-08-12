import json
from functions import wait, clear
from get import get
from time import sleep

#vars
global deviceName

def deviceList(ipAddress):
    deviceList = json.loads(get(ipAddress, 'devices').text)
    return deviceList

def singleDevice(ipAddress, menu):
    singleDeviceLoop = True
    while singleDeviceLoop:
        try:
            clear()
            print('List of devices:')
            print()
            devices = deviceList(ipAddress)
            devices.sort()
            deviceNum = 1
            maxDevices = len(devices)+1
            while deviceNum < maxDevices:
                deviceName = devices[deviceNum-1]
                alarms = json.loads(get(ipAddress, 'alarms?path='+devices[deviceNum-1]).content)
                i=0
                while i < len(alarms):
                    if alarms[i]['id']['name'] == "NAME" or alarms[i]['id']['name'] == "IDNAME":
                        deviceName = alarms[i]['state']['value']
                    i=i+1
                print(' ['+str(deviceNum)+'] '+str(devices[deviceNum-1])+' - '+str(deviceName))
                deviceNum = deviceNum+1
            print(' [.]')
            print(' [0] Return to '+menu)

            deviceSelect = int(input('Select Device number: '))
            deviceSelect = deviceSelect-1
            if 0 <= deviceSelect <= maxDevices:
                name = json.loads(get(ipAddress, 'alarms?path='+devices[deviceSelect]).content)
                i=0
                while i < len(alarms):
                    if alarms[i]['id']['name'] == "NAME" or alarms[i]['id']['name'] == "IDNAME":
                        deviceName = alarms[i]['state']['value']
                    i=i+1
                device = {"address": devices[deviceSelect], "name": deviceName}
                return device
            elif deviceSelect == -1:
                return {"device": None}
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