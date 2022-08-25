from getAlarms import selectDevice, displayAlarms, deviceList, getDeviceName
from functions import wait, clear, isGoodIPv4, focus
from publisher import createPublisher, setAlarm, maintainAlarms, removeAlarms, removePublisher, publishAllAlarms
from csvAlarms import csvWriter
from apiAccess import purge, delete
from subscriber import createSubscriber, getAlarmSubs, getSubscriber, subscribeAll
from time import sleep
import sys

# vars
subscriber = None
publisher = None
origin = None
deviceName = None
deviceAddress = None
alarmsCollected = False
titleName = '| (R)ead (O)rbit (A)larms and w(R)ite - roar.exe |'
title = len(titleName)*'-'+'\n'+titleName+'\n'+len(titleName)*'-'
# Exit tasks
def exitProgram(ipAddress, origin, subscriber):
    print('Cleaning up Publishers and Subscribers...')
    if origin != None:
        if removePublisher(ipAddress, origin).status_code == 204:
            print('Publishers removed.')
        else: print('Error removing Publisher.')
        sleep(0.5)
    if subscriber != None:
        data = None
        d = delete(ipAddress, 'subscribers?subscriptionId='+subscriber, data)
        print (d)
        if d.status_code == 204:
            print('Subscriber removed.')
        else: print('Error removing Subscriber.')
        sleep(0.5)
    print('Done.')
    sleep(0.5)
    # Final thing to do...
    clear()
    sys.exit()

# Help
def help():
    print('usage: roar [IP address of GV Orbit server] [device address]')
    sleep(0.25)
    print('Press any key to continue...')

# Main Menu
def mainMenu(gvoIP):
    global deviceName
    global deviceAddress
    global alarmsCollected
    global publisher
    global origin
    global subscriber
    mainMenuLoop = True
    while mainMenuLoop:
        try:
            clear()
            print(title)
            print()
            print('GV Orbit IP address: '+str(gvoIP))
            print('Subscriber: '+str(subscriber))
            print('Publisher: '+str(publisher))
            print('PublisherID: '+str(origin))
            print('Device: '+str(deviceName))
            print('Device address: '+str(deviceAddress))
            print('Alarms collected?: '+str(alarmsCollected))
            print()
            print('Main Menu')
            print()
            print(' [1] Set GV Orbit IP address')
            print(' [2] Collect Alarms')
            print(' [3] Publish Alarms')
            print(' [4] Live Alarm Data')
            print(' [.]')
            print(' [5] Purge Stale Data')
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
                # check IP address for gvoIP is set, run alarms menu if OK
                if gvoIP == None:
                    print('No GV Orbit server specified')
                    sleep(1)
                else:
                    publishAlarmsMenu(gvoIP)

            elif mainMenuSelect == 4:
                # check IP address for gvoIP is set, run alarms menu if OK
                if gvoIP == None:
                    print('No GV Orbit server specified')
                    sleep(1)
                else:
                    subscriberMenu(gvoIP)

            elif mainMenuSelect == 5:
                # check IP address for gvoIP is set, run alarms menu if OK
                if gvoIP == None:
                    print('No GV Orbit server specified')
                    sleep(1)
                else:
                    if purge(gvoIP).status_code == 200:
                        print('Removed stale alarm data.')
                        sleep(1)
                    else:
                        print('Error, check Monitoring service...')
                        sleep(1)

            elif mainMenuSelect == 0:
                #clear()
                #sys.exit()
                exitProgram(gvoIP,origin, subscriber)

        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to exit')
            print()
            sleep(1)

# Subscriber Menu
def subscriberMenu(gvoIP):
    # use global variables, not function variables
    global deviceAddress
    global deviceName
    global alarmsCollected
    global publisher
    global origin
    global subscriber
    menuName = 'Live Alarm Data Menu'

    subscriberMenuLoop = True
    while subscriberMenuLoop:
        try:
            clear()
            print(title)
            print()
            print('GV Orbit IP address: '+str(gvoIP))
            print('Subscriber: '+str(subscriber))
            print('Publisher: '+str(publisher))
            print('PublisherID: '+str(origin))
            print('Device: '+str(deviceName))
            print('Device address: '+str(deviceAddress))
            print('Alarms collected?: '+str(alarmsCollected))
            print()
            print(menuName)
            print()
            print(' [1] Create Alarm Subscriber, for specified devices')
            print(' [2] Create Alarm Subscriber, for all devices')
            print(' [.]')
            print(' [3] Show Live Data')
            print(' [.]')
            print(' [0] Return to Main Menu')
            print()

            subscriberMenuSelect = int(input('Select an option: '))
            if subscriberMenuSelect == 1:
                subscriber = createSubscriber(gvoIP)

            elif subscriberMenuSelect == 2:
                subscriber = subscribeAll(gvoIP)

            elif subscriberMenuSelect == 3:
                if subscriber != None:
                    # check if subscriber still exists
                    if getSubscriber(gvoIP, subscriber) == True: getAlarmSubs(gvoIP, subscriber)
                    else:
                        print('Subscriber not found or invalid.')
                        sleep(1)
                else:
                    print('Subscriber not created.')
                    sleep(1)

            elif subscriberMenuSelect == 0:
                subscriberMenuLoop = False
        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to return to Main Menu')
            print()
            sleep(1)

# Publisher Menu
def publishAlarmsMenu(gvoIP):
    # use global variables, not function variables
    global deviceAddress
    global deviceName
    global alarmsCollected
    global publisher
    global origin
    global subscriber
    menuName = 'Publish Alarms Menu'

    publishAlarmsMenuLoop = True
    while publishAlarmsMenuLoop:
        try:
            clear()
            print(title)
            print()
            print('GV Orbit IP address: '+str(gvoIP))
            print('Subscriber: '+str(subscriber))
            print('Publisher: '+str(publisher))
            print('PublisherID: '+str(origin))
            print('Device: '+str(deviceName))
            print('Device address: '+str(deviceAddress))
            print('Alarms collected?: '+str(alarmsCollected))
            print()
            print(menuName)
            print()
            print(' [1] Create Publisher')
            print(' [2] Maintain Publisher (do this after publishing alarms)')
            print(' [3] Publish Single Alarm')
            print(' [4] Publish CSV Alarm Data')
            print(' [.]')
            print(' [5] Remove All Alarms for current Publisher')
            print(' [6] Delete Publisher')
            print(' [.]')
            print(' [0] Return to Main Menu')
            print()

            publishAlarmsMenuSelect = int(input('Select an option: '))
            if publishAlarmsMenuSelect == 1:
                pub = createPublisher(gvoIP)
                publisher = pub['name']
                origin = pub['origin']

            elif publishAlarmsMenuSelect == 2:
                if publisher != None:
                    maintainAlarms(gvoIP, publisher, origin)
                else:
                    print('Publisher not created')
                    sleep(1)

            elif publishAlarmsMenuSelect == 3:
                if publisher != None:
                    deviceAddress = setAlarm(gvoIP, origin)
                else:
                    print('Publisher not created')
                    sleep(1)

            elif publishAlarmsMenuSelect == 4:
                if publisher != None:
                    publishAllAlarms(gvoIP, origin)
                else:
                    print('Publisher not created')
                    sleep(1)

            elif publishAlarmsMenuSelect == 5:
                if publisher != None:
                    removeAlarms(gvoIP, origin)
                else:
                    print('Publisher not created')
                    sleep(1)
                pass

            elif publishAlarmsMenuSelect == 6:
                if publisher != None:
                    removePublisher(gvoIP, origin)
                    origin = None
                    publisher = None
                else:
                    print('Publisher not created')
                    sleep(1)

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
    global origin
    global subscriber
    alarms = None
    menuName = 'Collect Alarms Menu'

    getAlarmsMenuLoop = True
    while getAlarmsMenuLoop:
        try:
            clear()
            print(title)
            print()
            print('GV Orbit IP address: '+str(gvoIP))
            print('Subscriber: '+str(subscriber))
            print('Publisher: '+str(publisher))
            print('PublisherID: '+str(origin))
            print('Device: '+str(deviceName))
            print('Device address: '+str(deviceAddress))
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
        else:
            help()
            wait()
            gvoIP = None
            deviceAddress = None

    # 2nd commandline argument is device address
    elif len(sys.argv)==3:
        # first check IP address is OK
        if isGoodIPv4(sys.argv[1]) == True:
            gvoIP = sys.argv[1]
            # now check if deviceAddress exists and return Name if it the name exists
            deviceAddress = sys.argv[2]
            deviceName = getDeviceName(deviceAddress, gvoIP)
        else: deviceName = None

    else:
        gvoIP = None
        deviceAddress = None
    
    # set window focus
    focus('roar')
    mainMenu(gvoIP)