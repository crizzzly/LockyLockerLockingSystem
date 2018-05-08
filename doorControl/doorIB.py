#!/usr/bin/env python
from subprocess import Popen, PIPE, STDOUT
import time
import smbus
import ctypes
import sys
import select
import tty
import termios
import RPi.GPIO as GPIO
import time
import datetime
import MySQLdb
import uinput
import os
import shutil
import io
import tempfile
import itertools

bus = smbus.SMBus(1)
address = 0x04
arduino = serial.Serial('/dev/ttyACM0', 9600)


host = "localhost"
user = "doorAccess"
password = "password"
db = "doorMaster"
#set up access to the mysql database using root due to permissions confusion, once permissions are fixed master may be used
db=MySQLdb.connect(host=host, user=user, passwd=password, db=db)
#add cursor which allows interaction with db
curs=db.cursor()
#don't even worry about this one
count=0
#save terminal settings so they can be reset after setting terminal to character mode
old_settings = termios.tcgetattr(sys.stdin.fileno())
#returns true if there is data int he sys.stdin buffer
def isData(proc):
    if proc.returncode() is not None:
        return True
    else:
        return False
    #return select.select([sys.stdin], [],[], 0) ==([sys.stdin], [], [])
#compares two time stamps to a second
def compareTimeStamps(time1, time2):
    year=[int(time1[0:4]), int(time2[0:4])]
    month=[int(time1[5:7]),int(time2[5:7])+(year[1]-year[0])*12]
    day=[int(time1[8:10]),int(time2[8:10])+(month[1]-month[0])*30]
    hour=[int(time1[11:13]),int(time2[11:13])+(day[1]-day[0])*24]
    minute=[int(time1[14:16]),int(time2[14:16])+(hour[1]-hour[0])*60]
    second=[int(time1[17:19]),int(time2[17:19])+(minute[1]-minute[0])*60]
    timeDifference=second[1]-second[0]
    return timeDifference
#returns the time of teh last status update
def getStatusTime():
    curs.execute("SELECT timestamp FROM status")
    readStat=curs.fetchall()
    time=readStat[0]
    return time
#gets current time in milliseconds
def getTime():
    millis = int(round(time.time() * 1000))
    return millis

#calls a few terminal commands to restart device
def restartDevice():
    cmd = 'sudo service udev restart'
    #cmd = 'sudo rmmod i2c_dev; sudo rmmod i2c_bcm2708; sudo rmmod i2c_2835'
    process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    process.wait()
    #cmd = 'sudo modprobe i2c_dev; sudo modprobe i2c_2708; sudo modprobe i2c_i2c_2835'
    #process= Popen(cmd, shell=True, stdin=PIPE,stdout=PIPE, stderr=STDOUT, close_fds=True)
    #process.wait()

#watches incoming data and times exit for complete card reads
def watchData():
    print("in watch data")
    cardReadData=""
    startReadTime=None#time reading started
    waitTimeMS=500#how long to wait if the buffer is empty
    timestamp=None#current timestamp
    isReading=False#true when readng is in progress
    deviceStoppedReadingTS=None#timestamp of when data buffer went empty after read started
    continueRead=True#true when reading should progress
    mysqlTS=getTime()#timestamp for use in logs
    error =0
    updateStatus("watching for data")#update the status table to reflet current action

    try:
        while continueRead:
            cmd = 'nfc-poll'
            process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            #wait until subprocess has finished
            process.wait()

            if(getTime()-mysqlTS>=10000):
                mysqlTS=getTime()
                updateStatus("in data watch cycle")

            startReadTime=getTime()#time reading started
            #read output of subprocess

            cardReadData= process.stdout.read()

            #if (process.stdout.read() is not NULL):

            #else:
            #    waitTimeMS=500#how long to wait if the buffer is empty

            if "ERROR" in str(cardReadData) or "error" in str(cardReadData):
                if error >2:
                    print (cardReadData)
                    restartDevice()
                    bus.close()
                    bus = smbus.SMBus(1)
                error = error +1
                time.sleep(0.5)

            else:
                error = 0
                continueRead = False
                deviceStoppedReadingTS=getTime()
                #print output
                print ("Data found: " + cardReadData)


    finally:
        return cardReadData



    #timestamp=None#current timestamp
    #isReading=False#true when readng is in progress
    #deviceStoppedReadingTS=None#timestamp of when data buffer went empty after read started
    #continueRead=True#true when reading should progress
    #mysqlTS=getTime()#timestamp for use in logs


#    if ("error" in str(cardReadData)) or ("unable" in str(cardReadData)) or ("nfc-poll" in str(cardReadData)):
#        restartDevice()
#
#    else:


def updateStatus(message):
    timestamp=make_timestamp()
    curs.execute("DELETE FROM status WHERE True=True")
    curs.execute("INSERT INTO status(status, timestamp) VALUES ('"+message+"', '"+ timestamp+"')")
    db.commit()

#checks if all  library functions are available. if not, resets the device
#get data from the card, truncate it, and then pass it to the handler function
def get_scan():
    card=watchData()
    if(card!=None):
        print("\nresult: "+card)
        handle_card(card)
    else:
        print("Bad read restarting")

#send array to arduino to open doors/lockers
def open_door(auth):

    #auth in db: 0, 1, 2
    #levels in db: authLevel0, authLevel1, authLevel2
    curs.execute("SELECT ('locker1','locker2','locker3') FROM accessRequest WHERE 'authLevel' = '1'")
    a = curs.fetchall()
    #create array from touple
    answer = list(itertools.chain.from_iterable(a))
    arduino.write(answer)




#make a new timestamp
def make_timestamp():
    ts=time.time()
    st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st

#check the card against the table of accepted cards to see if access is allowed, open door if allowed and log door openings
def check_card(card):
    curs.execute("SELECT * FROM acceptedCards")
    goodRead="door opened for: "
    for reading in curs.fetchall():
        if reading[1] == card:
            timestampAdd=make_timestamp()
            openedFor="Door opened for "+reading[2]
            curs.execute("INSERT INTO log(accessRequest, action, timestamp) VALUES ('"+card+"', '"+openedFor+"', '"+timestampAdd+"')")
            db.commit()
            #os.remove("/var/www/html/doorControl/Testing/devTest/androidM/index.html")
            open("/var/www/html/doorControl/Testing/index.html", 'w').close()
            shutil.copyfile("/var/www/html/doorControl/Testing/accessGranted.html", "/var/www/html/doorControl/Testing/index.html")
            return True

#check the card, if it's allowed open the door, if it's not then log an invalid entry attempt in the log
def handle_card(card):

    if check_card(card):
        curs.execute("SELECT authority FROM acceptedCards WHERE card='"+ card +"'")
        authorityRow=curs.fetchone()
        authority = authorityRow[0]
        print(authority)
        open_door(authority)
        time.sleep(1)#Change back to home page after auto refresh
        open("/var/www/html/doorControl/Testing/index.html", 'w').close()
        shutil.copyfile("/var/www/html/doorControl/Testing/main.html", "/var/www/html/doorControl/Testing/index.html")


    else:
        #os.remove("/var/www/html/doorControl/Testing/devTest/androidM/index.html")
        open("/var/www/html/doorControl/Testing/index.html", 'w').close()
        shutil.copyfile("/var/www/html/doorControl/Testing/accessDenied.html", "/var/www/html/doorControl/Testing/index.html")
        timestampAdd=make_timestamp()
        curs.execute("INSERT INTO log (accessRequest, action, timestamp) VALUES ('"+card+"', 'Invalid ID - Door Not Opened', '"+timestampAdd+"')")
        updateStatus("Bad read")
        db.commit()
        time.sleep(7)#Change back to home page after auto refresh
    	#os.remove("/var/www/html/doorControl/Testing/devTest/androidM/index.html")
        open("/var/www/html/doorControl/Testing/index.html", 'w').close()
        shutil.copyfile("/var/www/html/doorControl/Testing/main.html", "/var/www/html/doorControl/Testing/index.html")
    db.commit()

#never don't not stop scanning
def startProc():
    while True:
        get_scan()

startProc()
bus.close()
