from getAlarms import singleDevice
from functions import wait, clear, isGoodIPv4
from time import sleep

# vars
global gvoIP
global subscriber
global publisher
global deviceName
global deviceAddress

def mainMenu():
    mainMenuLoop = True
    gvoIP = None
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
            print(' [2] Get Alarms')
            print(' [.]')
            print(' [0] Exit')
            print()

            mainMenuSelect = int(input('Select an option: '))
            if mainMenuSelect == 1:
                gvoIPLoop = True
                while gvoIPLoop:
                    try:
                        gvoIP = input('Set GV Orbit IP address: ')
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
            print(' [1] Select single device')
            print(' [2] ')
            print(' [.]')
            print(' [0] Return to Main Menu')
            print()

            alarmsMenuSelect = int(input('Select an option: '))
            if alarmsMenuSelect == 1:
                deviceDetails = singleDevice(gvoIP, 'Alarms Menu')
                deviceAddress = deviceDetails["address"]
                deviceName = deviceDetails["name"]
            elif alarmsMenuSelect == 2:
                pass
            elif alarmsMenuSelect == 0:
                getAlarmsMenuLoop = False
        except (IndexError, ValueError) as e: # input error handling, can print(e) if required
            print()
            print ('Invalid selection.  Please use a number in the list.')
            print('Type [0] to return to Main Menu')
            print()
            sleep(1)

if __name__ == '__main__':
    deviceName = None
    deviceAddress = None
    subscriber = None
    publisher = None
    mainMenu()