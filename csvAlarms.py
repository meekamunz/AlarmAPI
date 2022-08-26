import csv
from functions import wait, clear, focus
from getAlarms import getDeviceName
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename

root=tk.Tk()
root.withdraw()

# csvWriter
def csvWriter(alarms, ipAddress):
    fileName = alarmsFile()
    f = open(fileName, 'w', newline='')
    writer = csv.writer(f)
    headers = ['Device Name', 'Address', 'Alarm', 'Time', 'State', 'Value', 'Latched State', 'Masked', 'Unmasked State', 'Inverted', 'Acknowledged', 'Acknowledged By']
    writer.writerow(headers)
    i=0
    cDev = None
    deviceName = None
    print('Writing alarms to '+fileName+'...')
    while i <len(alarms):
        currentDevice = alarms[i]['path']
        if cDev != currentDevice:
            cDev = currentDevice
            deviceName = getDeviceName(currentDevice, ipAddress)
        data = [deviceName, alarms[i]['path'], alarms[i]['name'], alarms[i]['timestamp'], alarms[i]['state'], alarms[i]['value'], alarms[i]['latchedState'], alarms[i]['masked'], alarms[i]['unmaskedState'], alarms[i]['inverted'], alarms[i]['acked'], alarms[i]['ackedBy']]
        writer.writerow(data)
        i=i+1
    f.close()

# select destination file
def alarmsFile():
    types = [('All tyes(*.*)', '*.*'),("csv file(*.csv)","*.csv")]
    outFile = asksaveasfilename(filetypes = types, defaultextension = types)
    focus('roar')
    return str(outFile)

# open csv file and convert to dictionary
def importCSV(origin):
    # open csv file as 'inFile'
    types = [('All tyes(*.*)', '*.*'),("csv file(*.csv)","*.csv")]
    inFile = askopenfilename(filetypes = types, defaultextension = types)

    # refocus to app window
    focus('roar')

    # convert inFile to alarm data
    with open (str(inFile), newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        i=0
        alarmData = []
        for row in reader:
            clear()
            if row[0] == 'Device Name':
                print('Skipping column headers...')
            else:
                # read columns into variables
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
                # user information
                print('Reading line '+str(i)+', Device: '+deviceName+', Alarm: '+alarm)

                # write variables as key:pairs
                data = {"id": {"name": str(alarm), "path": str(path)},"origin": str(origin),"state": {"acked": str(acked), "ackedBy": str(ackedBy), "inverted": str(inverted), "latchedState": str(latchedState), "masked": str(masked), "state": str(state), "timestamp": str(timestamp), "unmaskedState": str(unmaskedState), "value": str(value)}}
                alarmData.append(data)
            i=i+1
    return alarmData