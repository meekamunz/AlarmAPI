import msvcrt as m
import os

#clear screen
def clear():
    os.system('cls')

#wait for key press
def wait():
    m.getch()
    print('Where\'s the \'Any\' key?')

# check for IPv4 address
def isGoodIPv4(s):
    pieces = s.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False