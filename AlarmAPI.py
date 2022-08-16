from getAlarms import selectDevice, displayAlarms, deviceList, getDeviceName
from functions import wait, clear, isGoodIPv4
from publisher import createPublisher, setAlarm
from csvAlarms import csvWriter
from time import sleep
import sys

# vars
subscriber = None
publisher = None
deviceName = None
deviceAddress = None
alarmsCollected = False

# Main Menu
def mainMenu(gvoIP):
    global deviceName
    global deviceAddress
    global alarmsCollected
    global publisher
    mainMenuLoop = True
    while mainMenuLoop:
        try:
            clear()
            print('Current GV Orbit IP address: '+str(gvoIP))
            print('Current Subscriber: '+str(subscriber))
            print('Current Publisher: '+str(publisher))
            print('Current Device: '+str(deviceName))
            print('Current Device address: '+str(deviceAddress))
            print('Alarms collected?: '+str(alarmsCollected))
            print()
            print('Main Menu')
            print()
            print(' [1] Set GV Orbit IP address')
            print(' [2] Alarm Collection Menu')
            print(' [3] Alarm Publisher Menu')
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
            elif mainMenuSelect == 3:
                publishAlarmsMenu(gvoIP)
            elif mainMenuSelect == 0:
                clear()
                sys.exit()

        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to exit')
            print()
            sleep(1)

# Publisher Menu
def publishAlarmsMenu(gvoIP):
    # use global variables, not function variables
    global deviceAddress
    global deviceName
    global alarmsCollected
    global publisher
    menuName = 'Alarm Publisher Menu'

    publishAlarmsMenuLoop = True
    while publishAlarmsMenuLoop:
        try:
            clear()
            print('Current GV Orbit IP address: '+str(gvoIP))
            print('Current Subscriber: '+str(subscriber))
            print('Current Publisher: '+str(publisher))
            print('Current Device: '+str(deviceName))
            print('Current Device address: '+str(deviceAddress))
            print('Alarms collected?: '+str(alarmsCollected))
            print()
            print(menuName)
            print()
            print(' [1] Create Publisher')
            print(' [2] Publish Single Alarm')
            print(' [.]')
            print(' [0] Return to Main Menu')
            print()

            publishAlarmsMenuSelect = int(input('Select an option: '))
            if publishAlarmsMenuSelect == 1:
                pub = createPublisher(gvoIP)
                publisher = pub['name']
                origin = pub['origin']

            elif publishAlarmsMenuSelect == 2:
                setAlarm(gvoIP, origin)

            elif publishAlarmsMenuSelect == 0:
                publishAlarmsMenuLoop = False
        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to return to Main Menu')
            print()
            sleep(1)

# Alarms Menu
def getAlarmsMenu(gvoIP):
    # use global variables, not function variables
    global deviceAddress
    global deviceName
    global alarmsCollected
    global publisher
    alarms = None
    menuName = 'Alarm Collection Menu'

    getAlarmsMenuLoop = True
    while getAlarmsMenuLoop:
        try:
            clear()
            print('Current GV Orbit IP address: '+str(gvoIP))
            print('Current Subscriber: '+str(subscriber))
            print('Current Publisher: '+str(publisher))
            print('Current Device: '+str(deviceName))
            print('Current Device address: '+str(deviceAddress))
            print('Alarms collected?: '+str(alarmsCollected))
            print()
            print(menuName)
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
                deviceDetails = selectDevice(gvoIP, menuName)
                deviceAddress = deviceDetails["address"]
                deviceName = deviceDetails["name"]

            elif alarmsMenuSelect == 2:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, [deviceAddress], 'Fail')
                    alarmsCollected = True

            elif alarmsMenuSelect == 3:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, [deviceAddress], 'Warn')
                    alarmsCollected = True

            elif alarmsMenuSelect == 4:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, [deviceAddress], 'Ok')
                    alarmsCollected = True

            elif alarmsMenuSelect == 5:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, [deviceAddress], 'Unknown')
                    alarmsCollected = True

            elif alarmsMenuSelect == 6:
                if deviceAddress == None:
                    print ('No device specified')
                    sleep(1)
                else:
                    alarms = displayAlarms(gvoIP, [deviceAddress], 'all')
                    alarmsCollected = True

            elif alarmsMenuSelect == 7:
                alarms = displayAlarms(gvoIP, deviceList(gvoIP), 'Fail')
                alarmsCollected = True

            elif alarmsMenuSelect == 8:
                alarms = displayAlarms(gvoIP, deviceList(gvoIP), 'Warn')
                alarmsCollected = True

            elif alarmsMenuSelect == 9:
                alarms = displayAlarms(gvoIP, deviceList(gvoIP), 'Ok')
                alarmsCollected = True

            elif alarmsMenuSelect == 10:
                alarms = displayAlarms(gvoIP, deviceList(gvoIP), 'Unknown')
                alarmsCollected = True

            elif alarmsMenuSelect == 11:
                alarms = displayAlarms(gvoIP, deviceList(gvoIP), 'all')
                alarmsCollected = True

            elif alarmsMenuSelect == 12:
                # check if alarms have been gathered
                if alarms == None:
                    print('No alarms collected for device: '+str(deviceAddress)+' - '+str(deviceName))
                    sleep(1)
                else:
                    csvWriter(alarms, gvoIP)
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
    if len(sys.argv)==2:
        if isGoodIPv4(sys.argv[1]) == True:
            gvoIP = sys.argv[1]
        else: gvoIP = None
    else:
        gvoIP = None

    # 2nd commandline argument is device address
    if len(sys.argv)==3:
        # first check IP address is OK
        if isGoodIPv4(sys.argv[1]) == True:
            gvoIP = sys.argv[1]
            # now check if deviceAddress exists and return Name if it the name exists
            deviceAddress = sys.argv[2]
            deviceName = getDeviceName(deviceAddress, gvoIP)
        else:
            gvoIP = None
            deviceAddress = None
    else:
        if isGoodIPv4(sys.argv[1]) == True:
            gvoIP = sys.argv[1]
        else: gvoIP = None
        deviceAddress = None
    mainMenu(gvoIP)