import requests
import json

# vars
gvoIP = '10.96.240.100'
urlHead = 'http://' + gvoIP + ':9099/alarmapi/v1/'

# get all devices on system
allDevices = requests.get(urlHead + 'devices')

for device in json.loads(allDevices.text):
    # define a file friendly name and specify output directory
    friendlyName = device.replace(': ','_').replace('/','_').replace(' ','_').replace(':','_').replace('"','')
    outputDir = 'c:\\xfer\\GVO-AlarmApi\\processed\\'
    
    # get alarms for device
    alarms = json.loads(requests.get(urlHead + 'alarms?path=' + device).text)
    
    file = open(outputDir + friendlyName + '.txt', 'w')
    for alarm in alarms:
        # define file entries
        alarmName = alarm['id']['name']
        alarmState = alarm['state']['state']
        alarmData = alarm['state']['value']
        alarmTime = alarm['state']['timestamp']
        
        # convert alarmState to numerical value
        
        if alarmState == 'fail': alarmStateValue = 100
        elif alarmState == 'major': alarmStateValue = 75
        elif alarmState == 'minor': alarmStateValue = 50
        elif alarmState == 'warn': alarmStateValue = 50
        elif alarmState == 'ok': alarmStateValue = 1
        else: alarmStateValue = 0
        
        # define json string
        new_json = '{"alarm": "' + alarmName + '", "dataPoint": [{"alarmValue": "' + alarmData + '", "alarmTime": "' + alarmTime + '", "alarmState": , "' + str(alarmStateValue) + '"}]}'
        
        # output to file
        file.write(new_json + '\n')
    file.close()
