import json
from apiAccess import get, put, delete
from time import sleep

# deviceList
def deviceList(ipAddress):
    # list devices, then sort
    deviceList = json.loads(get(ipAddress, 'devices').text)
    deviceList.sort()
    return deviceList

# getDeviceAlarms
def getDeviceName(dAddress, ipAddress):
    # use name=NAME filter so server returns only the NAME alarm (not all alarms)
    try:
        name = json.loads(get(ipAddress, 'alarms?path='+dAddress+'&name=NAME').content)
    except Exception:
        return dAddress
    # if NAME exists, get device name for selected device
    deviceName=dAddress
    for alarm in name:
        if alarm['id']['name'] == "NAME":
            deviceName = alarm['state']['value']
            break
    return deviceName

# selectDevice
def selectDevice(ipAddress, menu):
    singleDeviceLoop = True
    while singleDeviceLoop:
        try:
            clear()
            print('List of devices:')
            print()
            devices = deviceList(ipAddress)
            # check for no devices
            if len(devices) == 0:
                print('No devices detected.  Check DDS domains on Alarm API and Mnitoring services.')
                wait()
                return {"address": None, "name": None}
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
                # return device with "name" and "address" key pairs
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
            #
        except (IndexError, ValueError) as e:# input error handling, can print(e) if required
            print()
            print('Invalid selection.  Please use a number in the list.')
            print('Type [0] to return to '+menu)
            print()
            sleep(1)
            pass

# displayAlarms — uses a temporary PULL subscriber to bulk-fetch all alarms
# instead of making N sequential /alarms?path= calls
def displayAlarms(ipAddress, deviceAddress, alarmLevel):
    # set alarm state filter values
    failValues = ['Critical', 'critical', 'Fail', 'FAIL', 'fail']
    warnValues = ['Warn', 'warn', 'WARN', 'Major', 'Minor', 'major', 'minor']
    okValues = ['OK', 'Ok', 'ok', 'normal']
    unknownValues = ['Unknown', 'UNKNOWN', 'NoState', 'Nostate', 'nostate', 'none', 'None', 'NONE']
    allValues = failValues + warnValues + okValues + unknownValues
    if alarmLevel in failValues: state = failValues
    elif alarmLevel in warnValues: state = warnValues
    elif alarmLevel in okValues: state = okValues
    elif alarmLevel in unknownValues: state = unknownValues
    else: state = allValues

    # Convert device addresses to filter format
    deviceSet = set(deviceAddress)
    filters = [{'path': addr} for addr in deviceAddress]

    # Try subscription-based bulk fetch (3 API calls instead of N)
    try:
        # Create temporary PULL subscriber filtered to these devices
        sub_data = {'type': 'pull', 'filter': filters}
        sub_resp = put(ipAddress, 'subscribers', sub_data)
        sub_id = sub_resp.content.decode('utf-8').strip().strip('"')

        # Pull initial alarm dump — server delivers all current alarms on first poll
        changes_resp = get(ipAddress, 'alarms/changes?subscriptionId=' + sub_id)

        # Clean up subscriber immediately
        try:
            delete(ipAddress, 'subscribers?subscriptionId=' + sub_id, None)
        except Exception:
            pass

        if changes_resp.status_code == 200:
            events = json.loads(changes_resp.content)
            alarms = []
            for item in events.get('items', []):
                alarm = item.get('update')
                if alarm and alarm['id']['path'] in deviceSet:
                    if alarm['state']['state'] in state:
                        alarms.append({
                            'name': alarm['id']['name'],
                            'path': alarm['id']['path'],
                            'state': alarm['state']['state'],
                            'acked': alarm['state'].get('acked', False),
                            'ackedBy': alarm['state'].get('ackedBy', ''),
                            'inverted': alarm['state'].get('inverted', False),
                            'latchedState': alarm['state'].get('latchedState', ''),
                            'masked': alarm['state'].get('masked', False),
                            'timestamp': alarm['state'].get('timestamp', ''),
                            'unmaskedState': alarm['state'].get('unmaskedState', ''),
                            'value': alarm['state'].get('value', '')
                        })
            return alarms
    except Exception:
        pass

    # Fallback: sequential per-device fetching if subscription approach fails
    alarms = []
    for addr in deviceAddress:
        try:
            results = json.loads(get(ipAddress, 'alarms?path=' + str(addr)).content)
            for r in results:
                if r['state']['state'] in state:
                    alarms.append({
                        'name': r['id']['name'], 'path': r['id']['path'],
                        'state': r['state']['state'], 'acked': r['state']['acked'],
                        'ackedBy': r['state']['ackedBy'], 'inverted': r['state']['inverted'],
                        'latchedState': r['state']['latchedState'], 'masked': r['state']['masked'],
                        'timestamp': r['state']['timestamp'], 'unmaskedState': r['state']['unmaskedState'],
                        'value': r['state']['value']
                    })
        except Exception:
            pass
    return alarms