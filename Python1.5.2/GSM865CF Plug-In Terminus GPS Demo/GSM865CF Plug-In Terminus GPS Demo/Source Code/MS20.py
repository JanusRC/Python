#External GPS Class Example
# Written for NavSync's MS20 GPS Receiver
# Goto:  www.navsync.com for more information
#
#Copyright © 2011, Janus Remote Communications
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#
#Redistributions of source code must retain the above copyright notice,
#this list of conditions and the following disclaimer.
#
#Redistributions in binary form must reproduce the above copyright
#notice, this list of conditions and the following disclaimer in
#the documentation and/or other materials provided with the distribution.
#
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS``AS
#IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Written By Thomas W. Heck
##  MODULE:
##      MS20.py
##  REVISION HISTORY:
##      1.0   04/22/2011  TWH --  Init Release
##

import MOD              #code owned by: Telit
import sys              #code owned by: Telit
import timers           #code owned by: Telit
import SER2             #code owned by: Telit

class GPSdata:
    GPGGA = ''
    GPGLL = ''
    GPGSA = ''
    GPGSV = ''
    GPRMC = ''
    GPZDA = ''
    GPVTG = ''
    NMEA = ''
    HW_VER = ''
    APP_VER = ''
    KERNEL_VER = ''
    POLLED_CMD = ''

def initGPS (speed,format):
    
    # Method return value:
    #   -6 = Unknown error
    #   -5 = Incorrect NMEA command response
    #   -4 = No NMEA Command response
    #   -3 = NMEA Command response Checksum fail
    #   -1 = Exception occurred
    #    0 = Finished w/o error
    #   >0 = NMEA Command response error value

    tmpReturn = -1

    try:

        #Init Serial Port Settings
        res = SER2.set_speed(speed,format)
        if not(res == 1):
            return -6

        #Clear NMEA Buffer
        GPSdata.NMEA = SER2.read()
        GPSdata.NMEA = ''

        res = pollNMEA('8',2)
        tmpReturn = res

    except:
        printException("initGPS()")
        tmpReturn = -1
        
    return tmpReturn

def getNMEA ():
    
    # Method return value:
    #   -1 = Exception occurred
    #    0 = Finished w/o error

    tmpReturn = -1

    try:

        #Build NMEA buffer
        GPSdata.NMEA = GPSdata.NMEA + SER2.read()

        tmpReturn = 0       

    except:
        printException("getNMEA()")
        tmpReturn = -1
        
    return tmpReturn

def sendNmeaCmd (inSTR1, inSTR2):

    # Method return value:
    #   -5 = Incorrect NMEA command response
    #   -4 = No NMEA Command response
    #   -3 = NMEA Command response Checksum fail
    #   -1 = Exception occurred
    #    0 = Finished w/o error
    #   >0 = NMEA Command response error value

    # inSTR1 = MS20 NMEA command
    # inSTR2 = MS20 NMEA command data

    tmpReturn = -1

    try:

        #Build NMEA command
        #Calculate NMEA checksum
        y = inSTR1 + inSTR2
        x = calcChecksum (y[1:len(y)])
        #Format NMEA sentence
        y = y + '*' + x + '\r\n'

        #Send NMEA command
        res = SER2.send(y)      

        #Evaluate NMEA command response
        res = getNextSentence(inSTR1, 2)

        print 'NMEA Command Sent: ' + y
        if not(res == 0):
            print 'NMEA Command failed!'
            print '  Return Code: ' + str(res)
            # pass return code back to calling method
            tmpReturn = res
        else:

            tmpReturn = 0

    except:
        printException("sendNmeaCmd()")
        tmpReturn = -1

    return tmpReturn
def getNextSentence (inSTR1,timeOut):

    # Method return value:
    #   -5 = Incorrect NMEA command response
    #   -4 = No NMEA Command response
    #   -3 = NMEA Command response Checksum fail
    #   -1 = Exception occurred
    #    0 = Finished w/o error

    tmpReturn = -1

    # Method inputs:
    #    inSTR$:
    #       Any valid NMEA $GP sentence
    #       Any valid $PMST command response data
    #   timeOut:
    #       1 to 10 = Select all NMEA sentences

    try:

        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(timeOut)
        
        while(1):

            #Build NMEA Buffer
            res = getNMEA()

            pos1 = -1
            pos2 = -2

            if ((inSTR1[0:5] == '$PMST')and not(inSTR1[0:len(inSTR1)] == '$PMST100')):
                #Pull First $PMST200 command ack message
                pos1 = GPSdata.NMEA.find('$PMST200',0,len(GPSdata.NMEA))
                
            else:
                #Pull first specified sentence
                pos1 = GPSdata.NMEA.find(inSTR1,0,len(GPSdata.NMEA))

            #If $PMST200 command present look for end of message
            if pos1 > -1:
                pos2 = GPSdata.NMEA.find('\r\n',pos1,len(GPSdata.NMEA))

            #Grab command ack from NMEA buffer
            if ((pos1 > -1) and (pos2 > -1)):
                y = GPSdata.NMEA[pos1:pos2 + 2]
                GPSdata.POLLED_CMD = GPSdata.NMEA[pos1:pos2+2]
                GPSdata.NMEA = GPSdata.NMEA[pos2 + 2:len(GPSdata.NMEA)]
                break

            if timerA.isexpired():
                break

        if not(timerA.isexpired()):
            #Is NMEA command checksum good?
            x = calcChecksum (y[1:len(y)-5])
            if not(x == y[len(y)-4:len(y)-2]):
                GPSdata.POLLED_CMD = ''
                return -3

            if ((inSTR1[0:5] == '$PMST')and not(inSTR1[0:len(inSTR1)] == '$PMST100')):
                #Is correct response?
                list = y.split(',')
                if not(inSTR1 == '$PMST' + list[1]):
                   return -5

                #Is there an error response?
                list = list[2].split('*')
                if not(list[0] == ''):
                   tmpReturn = list[0]
                else:
                    tmpReturn = 0
            else:
                #Is correct response?
                list = y.split(',')
                if not(inSTR1 == list[0]):
                    GPSdata.POLLED_CMD = ''
                    return -5
                else:
                    tmpReturn = 0

        else:
            # No NMEA command response
            tmpReturn = -4

    except:
        printException("getNextSentence()")
        tmpReturn = -1

    return tmpReturn

def calcChecksum (inSTR):

    tmpReturn = -1

    try:

        Checksum = 0
        for x in inSTR:           
            Checksum = Checksum ^ ord(x)

        tmpReturn = str(hex(Checksum))[2:4].upper()
        if len(tmpReturn) != 2:
            tmpReturn = '0' + tmpReturn

    except:
        printException("calcChecksum()")
        tmpReturn = -1

    return tmpReturn

def setNmeaRate (inSTR1,inSTR2):

    # Method return value:
    #   -5 = Incorrect NMEA command response
    #   -4 = No NMEA Command response
    #   -3 = NMEA Command response Checksum fail
    #   -2 = Invalid inputs
    #   -1 = Exception occurred
    #    0 = Finished w/o error
    #   >0 = NMEA Command response error value

    # Method inputs:
    #   inSTR1:
    #       -1 = Select all NMEA sentences
    #        0 = Select GPRMC sentence
    #        1 = Select GPGGA sentence
    #        2 = Select GPGLL sentence
    #        3 = Select GPGSA sentence
    #        4 = Select GPGSV sentence
    #        6 = Select GPVTG sentence
    #        7 = Select GPZDA sentence
    #   inSTR2:
    #        0 = Disable NMEA sentence transmit
    #        4 = Transmit once every 1 second
    #        5 = Transmit once every 2 seconds
    #        6 = Transmit once every 3 seconds
    #        7 = Transmit once every 4 seconds
    #        8 = Transmit once every 5 seconds
    #        9 = Transmit once every 10 seconds
    #        A = Transmit once every 15 seconds
    #        B = Transmit once every 20 seconds
    #        C = Transmit once every 30 seconds
    #        D = Transmit once every 60 seconds

    tmpReturn = -1

    try:

        # Check if method inputs are valid
        LIST1 = ['-1','0','1','2','3','4','6','7']
        tmpReturn = -2
        for x in LIST1:
            if (x == inSTR1):
                tmpReturn = -1
                break

        if (tmpReturn == -2):
            return -2
        
        LIST1 = ['0','4','5','6','7','8','9','A','B','C','D']
        tmpReturn = -2
        for x in LIST1:
            if (x == inSTR2):
                tmpReturn = -1
                break

        if (tmpReturn == -2):
            return -2
                   
        # Send $PMST12 command to set NMEA sentence Periodicity
        if (inSTR1 == '-1'):
            LIST1 = ['0','1','2','3','4','6','7']
            for x in LIST1:
                #Update all NMEA sentences
                y = ',' + x + ',' + inSTR2
                res = sendNmeaCmd('$PMST12',y)
                if not(res==0):
                    return res

            tmpReturn = 0

        else:
            #Disable an NMEA sentences
            y = ',' + inSTR1 + ',' + inSTR2
            res = sendNmeaCmd('$PMST12',y)
            tmpReturn = res

    except:
        printException("setNmeaRate()")
        tmpReturn = -1

    return tmpReturn

def pollNMEA (inSTR1,timeOut):

    # Method return value:
    #   -5 = Incorrect NMEA command response
    #   -4 = No NMEA Command response
    #   -3 = NMEA Command response Checksum fail
    #   -2 = Invalid inputs
    #   -1 = Exception occurred
    #    0 = Finished w/o error
    #   >0 = NMEA Command response error value

    # Method inputs:
    #   inSTR1:
    #       Any valid NMEA sentence and $PMST100
    #   timeOut:
    #       1 to 10 = Select all NMEA sentences

    tmpReturn = -1

    try:

        # Method input parameters valid?
        LIST1 = ['0,$GPRMC','1,$GPGGA','2,$GPGLL','3,$GPGSA','4,$GPGSV','6,$GPVTG','7,$GPZDA','8,$PMST100']
        tmpReturn = -2
        for x in LIST1:
            y = str(x)
            y = y.split(',')[0]                     #Store Command Index
            if (y == inSTR1):
                tmpReturn = -1
                z = str(x)
                z = z.split(',')[1]                 #Store polled sentence
                break

        if (tmpReturn == -2):
            return -2

        if not(0 <= timeOut <= 10):
            return -2

        # Method input parameters are valid

        #Poll GPGLL NMEA sentence
        res = sendNmeaCmd('$PMST14',',' + y)
        if (res == 0):
            #Grab NMEA sentence from NMEA buffer
         
            res = getNextSentence (z,5)
            
            if (res == 0):
                if (y == '0'):
                    GPSdata.GPRMC = GPSdata.POLLED_CMD
                    GPSdata.POLLED_CMD = ''
                elif (y == '1'):
                    GPSdata.GPGGA = GPSdata.POLLED_CMD
                    GPSdata.POLLED_CMD = ''
                elif (y == '2'):
                    GPSdata.GPGLL = GPSdata.POLLED_CMD
                    GPSdata.POLLED_CMD = ''
                elif (y == '3'):
                    GPSdata.GPGSA = GPSdata.POLLED_CMD
                    GPSdata.POLLED_CMD = ''
                elif (y == '4'):
                    #Get all GSV sentences
                    GPSdata.GPGSV = GPSdata.POLLED_CMD
                    x = int(GPSdata.POLLED_CMD.split(',')[1])-1
                    while(x > 0):
                        res = getNextSentence (z,5)
                        if (res == 0):
                            GPSdata.GPGSV = GPSdata.GPGSV + GPSdata.POLLED_CMD
                            x = x -1
                        else:
                            x = 0
                    
                    GPSdata.POLLED_CMD = ''
                elif (y == '6'):
                    GPSdata.GPVTG = GPSdata.POLLED_CMD
                    GPSdata.POLLED_CMD = ''
                elif (y == '7'):
                    GPSdata.GPZDA = GPSdata.POLLED_CMD
                    GPSdata.POLLED_CMD = ''
                elif (y == '8'):
                    x = GPSdata.POLLED_CMD.split(',')
                    GPSdata.HW_VER = x[1] + '.' + x[2]
                    GPSdata.APP_VER = x[3] + '.' + x[4]
                    GPSdata.KERNEL_VER = x[7] + '.' + x[8]
                    GPSdata.POLLED_CMD = ''

                tmpReturn = 0

        else:
            tmpReturn = res

    except:
        printException("pollGPGLL()")
        tmpReturn = -1

    return tmpReturn

def printException(methodName):

    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> MS20"
    print "METHOD -> " + methodName

    return
