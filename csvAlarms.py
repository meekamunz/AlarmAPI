import csv
import json as jsonlib
from getAlarms import getDeviceName
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename

# csvWriter — write alarms to CSV; if fileName is None, show file dialog
def csvWriter(alarms, ipAddress, fileName=None):
    if fileName is None:
        types = [("csv file(*.csv)","*.csv"), ('All types(*.*)', '*.*')]
        fileName = asksaveasfilename(filetypes=types, defaultextension=types)
        if not fileName:
            return None
    f = open(fileName, 'w', newline='')
    writer = csv.writer(f)
    headers = ['Device Name', 'Address', 'Alarm', 'Time', 'State', 'Value', 'Latched State', 'Masked', 'Unmasked State', 'Inverted', 'Acknowledged', 'Acknowledged By']
    writer.writerow(headers)
    cDev = None
    deviceName = None
    for alarm in alarms:
        currentDevice = alarm['path']
        if cDev != currentDevice:
            cDev = currentDevice
            deviceName = getDeviceName(currentDevice, ipAddress)
        data = [deviceName, alarm['path'], alarm['name'], alarm['timestamp'], alarm['state'], alarm['value'], alarm['latchedState'], alarm['masked'], alarm['unmaskedState'], alarm['inverted'], alarm['acked'], alarm['ackedBy']]
        writer.writerow(data)
    f.close()
    return fileName

# jsonWriter — write alarms to JSON; if fileName is None, show file dialog
def jsonWriter(alarms, ipAddress, fileName=None):
    if fileName is None:
        types = [("json file(*.json)","*.json"), ('All types(*.*)', '*.*')]
        fileName = asksaveasfilename(filetypes=types, defaultextension=types)
        if not fileName:
            return None
    with open(fileName, 'w') as f:
        jsonlib.dump(alarms, f, indent=2)
    return fileName

# importCSV — read CSV into alarm data list; if filePath is None, show file dialog
def importCSV(origin, filePath=None):
    if filePath is None:
        types = [("csv file(*.csv)","*.csv"), ('All types(*.*)', '*.*')]
        filePath = askopenfilename(filetypes=types, defaultextension=types)
        if not filePath:
            return []
    with open(str(filePath), newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        alarmData = []
        for row in reader:
            if row[0] == 'Device Name':
                continue
            deviceName = row[0]
            path = row[1]
            alarm = row[2]
            timestamp = row[3]
            state = row[4]
            value = row[5]
            latchedState = row[6]
            masked = row[7]
            unmaskedState = row[8]
            inverted = row[9]
            acked = row[10]
            ackedBy = row[11]
            data = {"id": {"name": str(alarm), "path": str(path)},"origin": str(origin),"state": {"acked": str(acked), "ackedBy": str(ackedBy), "inverted": str(inverted), "latchedState": str(latchedState), "masked": str(masked), "state": str(state), "timestamp": str(timestamp), "unmaskedState": str(unmaskedState), "value": str(value)}}
            alarmData.append(data)
    return alarmData

# importJSON — read JSON alarm file; if filePath is None, show file dialog
def importJSON(origin, filePath=None):
    if filePath is None:
        types = [("json file(*.json)","*.json"), ('All types(*.*)', '*.*')]
        filePath = askopenfilename(filetypes=types, defaultextension=types)
        if not filePath:
            return []
    with open(str(filePath)) as f:
        rawAlarms = jsonlib.load(f)
    # Re-stamp with given origin
    alarmData = []
    for alarm in rawAlarms:
        data = {"id": {"name": alarm['name'], "path": alarm['path']}, "origin": str(origin), "state": {"acked": str(alarm.get('acked','')), "ackedBy": str(alarm.get('ackedBy','')), "inverted": str(alarm.get('inverted','')), "latchedState": str(alarm.get('latchedState','')), "masked": str(alarm.get('masked','')), "state": str(alarm.get('state','')), "timestamp": str(alarm.get('timestamp','')), "unmaskedState": str(alarm.get('unmaskedState','')), "value": str(alarm.get('value',''))}}
        alarmData.append(data)
    return alarmData