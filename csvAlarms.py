import csv
from getAlarms import getDeviceName
from tkinter.filedialog import asksaveasfile, asksaveasfilename

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
    data = [('All tyes(*.*)', '*.*'),("csv file(*.csv)","*.csv")]
    outFile = asksaveasfilename(filetypes = data, defaultextension = data)
    return str(outFile)