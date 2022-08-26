Run roar.exe either from a File Explorer window or from command line.  If running from command line, you can optionally append the GV Orbit server IP Address and a device address on the commandline:
roar [IP address of GV Orbit server] [device address]

If you want to append a device address, you have to append the IP address first.  You can append the IP address on its own if you wish.

This tool can perform the following tasks:
- read alarms from a GV Orbit Alarm API instance
- save those alarms to a CSV file
- write a single alarm to a GV Orbit Alarm API instance
- write a CSV list of alarms to a GV Orbit Alarm API instance.  The CSV file data must be in the following format:
	Device Name,Address,Alarm,Time,State,Value,Latched State,Masked,Unmasked,State,Inverted,Acknowledged,Acknowledged By,
- maintain published alarms
- purge stale alarms
- view live alarm data

Michael.Munns@grassvalley.com