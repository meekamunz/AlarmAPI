import sqlite3, json
from sqlite3 import Error
from functions import wait, clear, focus
from tkinter.filedialog import asksaveasfilename, askopenfilename

# file and location
def dbFile():
    types = [('All tyes(*.*)', '*.*'),("db file(*.db)","*.db")]
    outFile = asksaveasfilename(filetypes = types, defaultextension = types)
    #focus('roar')
    return str(outFile)

# create database
def createConnection():
    conn = None
    dbFile = dbFile()
    try:
        conn = sqlite3.connect(dbFile)
        print(str(dbFile) + ' created.')
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

# import json data to database
def sqlDataImport(jsonData, database):
    if database == None:
        dbFile = createConnection()
    else: dbFile = database
    connection = sqlite3.connect(dbFile)
    cursor = connection.cursor()
    traffic = json.load(jsonData)

    columns = ['name', 'path', 'origin', 'acked', 'ackedBy', 'inverted', 'latchedState', 'masked', 'state', 'timestamp', 'unmaskedState', 'value']


    #traffic = json.load(open('json_file.json'))
    #columns = ['name','course','roll']
    #for row in traffic:
    #    keys= tuple(row[c] for c in columns)
    #    cursor.execute('insert into Student values(?,?,?)',keys)
    #    print(f'{row["name"]} data inserted Succefully')
    #
    #connection.commit()
    #connection.close()

    return database

if __name__ == '__main__':
    createConnection()