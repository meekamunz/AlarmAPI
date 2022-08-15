from getAlarms import selectDevice, displayAlarms, deviceList
from functions import wait, clear, isGoodIPv4
from get import get
from csvAlarms import csvWriter
from time import sleep
import sys
import json

# vars
subscriber = None
publisher = None
deviceName = None
deviceAddress = None

def mainMenu(gvoIP):
    global deviceName
    global deviceAddress
    mainMenuLoop = True
    while mainMenuLoop:
        try:
            clear()
            print('Current GV Orbit IP address: '+str(gvoIP))
            print('Current Subscriber: '+str(subscriber))
            print('Current Publisher: '+str(publisher))
            print('Current Device: '+str(deviceName))
            print('Current Device address: '+str(deviceAddress))
            print()
            print('Main Menu')
            print()
            print(' [1] Set GV Orbit IP address')
            print(' [2] Alarms Menu')
            print(' [.]')
            print(' [0] Exit')
            print()

            mainMenuSelect = int(input('Select an option: '))
            if mainMenuSelect == 1:
                gvoIPLoop = True
                while gvoIPLoop:
                    try:
                        gvoIP = input('Set GV Orbit IP address: ')
                        # check valid IP address
                        if isGoodIPv4(gvoIP) == True: 
                            gvoIPLoop = False
                        else:
                            print('Invalid IP address, please try again...')
                            sleep(2)
                            gvoIP = None
                            continue
                    except(ValueError):
                        print('Invalid IP address, please try again...')
                        sleep(2)
                        gvoIP = None
                        pass
            elif mainMenuSelect == 2:
                # check IP address for gvoIP is set, run alarms menu if OK
                if gvoIP == None:
                    print('No GV Orbit server specified')
                    sleep(1)
                else:
                    getAlarmsMenu(gvoIP)
            elif mainMenuSelect == 0:
                clear()
                sys.exit()

        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to exit')
            print()
            sleep(1)

def getAlarmsMenu(gvoIP):
    # use global variables, not function variables
    global deviceAddress
    global deviceName
    alarms = None

    getAlarmsMenuLoop = True
    while getAlarmsMenuLoop:
        try:
            clear()
            print('Current GV Orbit IP address: '+str(gvoIP))
            print('Current Subscriber: '+str(subscriber))
            print('Current Publisher: '+str(publisher))
            print('Current Device: '+str(deviceName))
            print('Current Device address: '+str(deviceAddress))
            print()
            print('Alarms Menu')
            print()
            print(' [1] Select device')
            print(' [.]')
            print(' [2] Get current Critical alarms for current device')
            print(' [3] Get current Major/Minor alarms for current device')
            print(' [4] Get current Ok alarms for current device')
            print(' [5] Get current Unknown alarms for current device')
            print(' [6] Get all alarms for current device')
            print(' [.]')
            print(' [7] Get current Critical alarms for all devices')
            print(' [8] Get current Major/Minor alarms for all devices')
            print(' [9] Get current Ok alarms for all devices')
            print(' [10] Get current Unknown alarms for all devices')
            print(' [11] Get all alarms for all devices')
            print(' [.]')
            print(' [12] Save alarms to CSV file')
            print(' [.]')
            print(' [0] Return to Main Menu')
            print()

            alarmsMenuSelect = int(input('Select an option: '))
            if alarmsMenuSelect == 1:
                deviceDetails = selectDevice(gvoIP, 'Alarms Menu')
                deviceAddress = deviceDetails["address"]
                deviceName = deviceDetails["name"]

            elif alarmsMenuSelect == 2:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, deviceAddress, 'Fail')

            elif alarmsMenuSelect == 3:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, deviceAddress, 'Warn')

            elif alarmsMenuSelect == 4:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, deviceAddress, 'Ok')

            elif alarmsMenuSelect == 5:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, deviceAddress, 'Unknown')

            elif alarmsMenuSelect == 6:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, deviceAddress, 'all')

            elif alarmsMenuSelect == 12:
                # check if alarms have been gathered
                if alarms == None:
                    print('No alarms collected for device: '+str(deviceAddress)+' - '+str(deviceName))
                    sleep(1)
                else:
                    if deviceName != None:
                        csvWriter(alarms, deviceName)
                    else: csvWriter(alarms, deviceAddress)
            elif alarmsMenuSelect == 0:
                getAlarmsMenuLoop = False
        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to return to Main Menu')
            print()
            sleep(1)

if __name__ == '__main__':
    # 1st commandline argument is GVO IP address
    if len(sys.argv)>1:
        if isGoodIPv4(sys.argv[1]) == True:
            gvoIP = sys.argv[1]
        else: gvoIP = None
    else:
        gvoIP = None

    # 2nd commandline argument is device address
    if len(sys.argv)>2:
        # first check IP address is OK
        if isGoodIPv4(sys.argv[1]) == True:
            gvoIP = sys.argv[1]
            # now check if deviceAddress exists
            dAddress = sys.argv[2]
            if dAddress in deviceList(gvoIP):
                deviceAddress = dAddress
                name = json.loads(get(gvoIP, 'alarms?path='+deviceAddress).content)
                # if NAME or IDNAME exists, get device name for selected device
                i=0
                while i < len(name):
                    if name[i]['id']['name'] == "NAME" or name[i]['id']['name'] == "IDNAME":
                        deviceName = name[i]['state']['value']
                    i=i+1
            else:
                deviceAddress = None
        else:
            gvoIP = None
            deviceAddress = None
    else:
        gvoIP = None
        deviceAddress = None
    mainMenu(gvoIP)