import msvcrt as m
import os, re
from time import sleep
from json import JSONEncoder
import pygetwindow as gw

# JSONEncoder
class DateTimeEncoder(JSONEncoder):
    #Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

#clear screen
def clear():
    os.system('cls')

#wait for key press
def wait():
    print('Press any key to continue...')
    m.getch()
    print('Where\'s the \'Any\' key?')

# check for IPv4 address
def isGoodIPv4(s):
    pieces = s.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False

# set window focus
def focus(windowName):
    titles = gw.getAllTitles()
    search = re.compile('.*'+windowName+'.*')
    match = [string for string in titles if re.match(search, string)]
    window = gw.getWindowsWithTitle(match[0])[0]
    # pygetwindow activate the handle is invalid
    window.minimize()
    window.restore()