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
##      ATC.py
##  REVISION HISTORY:
##      1.0     01/01/2007  TWH --  Init Release
##      1.1     05/02/2008  TWH --  Changed the method for Command Timeout (using timers.pyo method)
##      1.2     04/24/2009  TWH --  Added printException method to reduce code space.
##

import MDM      #code owned by: Telit
import MOD      #code owned by: Telit
import timers   #code owned by: Telit
import sys      #code owned by: Telit

class properties:
    IMEI = ''
    SIM = ''
    Carrier = ''
    CellId = ''
    CMD_TERMINATOR = 'OK\r\n'    # This is the string termination of a AT command response
    firmwareMajor = ''
    firmwareMinor = ''
    firmwareRevision = ''
    firmwareModel = ''

################################################################################################
## Methods for sending and receiving AT Commands
################################################################################################
    
def sendAtCmd(theCommand, theTerminator, retry, timeOut):
# This function sends an AT command to the MDM interface

    # Input Parameter Definitions
    #   theCommand: The AT command to send to MDM interface
    #   theTerminator: string or character at the end of AT Command
    #   retry:  How many times the command will attempt to retry if not successfully send 
    #   timeOut: number of [1/10 seconds] command could take to respond

    try:

        #Clear input buffer
        res = "junk"
        while(res != ""):
            res = MDM.receive(1)

        while (retry != -1):
            print 'Sending AT Command: ' + theCommand
            res = MDM.send(theCommand, 0)
            res = MDM.sendbyte(0x0d, 0)

            #Wait for AT command response
            res = mdmResponse(theTerminator, timeOut)

            #Did AT command respond without error?    
            pos1 = res.rfind(theTerminator,0,len(res))
            if (pos1 != -1):
                retry = -1
                res = parseResponse(res)
            else:
                retry = retry - 1

    except:
        printException("sendAtCmd()")

    print res

    return res

def mdmResponse(theTerminator, timeOut):
# This function waits for AT Command response and handles errors and ignores unsolicited responses

  # Input Parameter Definitions
  #   theTerminator: string or character at the end of a received string that indicates end of a response
  #   timeOut: number of seconds command could take to respond

    try:

        print 'Waiting for AT Command Response'

        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(timeOut)

        #Wait for response
        res = ''
        while ((res.find(theTerminator)<=-1) and (res.find("ERROR")<=-1) and (res != 'timeOut')):
            MOD.watchdogReset()
            res = res + MDM.receive(10)

            pass            
            if timerA.isexpired():
                res = 'timeOut'

    except:
        printException("mdmResponse()")

    return res

def parseResponse(inSTR):
# This function parses out data return from AT commands

  # Input Parameter Definitions
  #   inSTR:  The response string from and AT command

    try:

        tmpReturn = ''
        lenght = len(inSTR)

        if lenght != 0:
            pos1 = inSTR.find('ERROR',0,lenght)
            if (pos1 != -1):
                tmpReturn = 'ERROR'
            else:
                list_in = inSTR.split( '\r\n' )
                tmpReturn = list_in[ 1 ]

    except:
        printException("parseResponse()")

    return tmpReturn

################################################################################################
## Misc. Methods for GSM Modules
################################################################################################

def reboot():
# This method does return a response.  After the AT#REBOOT command executes the GSM module will
# reset and the script will restart depending on the #STARTMODESCR settings.

    MOD.sleep(15)                                               #required to halt Python thread and allow NVM Flash to update
    print "Rebooting Terminus!"
    sendAtCmd('AT#REBOOT',properties.CMD_TERMINATOR,0,20)

    return

def getFirmwareRev():

    tmpReturn = -1

    try:
        res = sendAtCmd("AT+CGMR",properties.CMD_TERMINATOR,0,2)                #query firmware revision
        parts = res.split(".")

        properties.firmwareMajor = parts[0]
        properties.firmwareMinor = parts[1]
        properties.firmwareRevision = parts[2][2]
        properties.firmwareModel = parts[2][0] + parts[2][1]

        tmpReturn = 0

    except:
        printException("getFirmwareRev()")

    return tmpReturn

def getNetworkInfo():

    try:
        properties.SIM = ""
        properties.SIM = sendAtCmd('AT+CIMI',properties.CMD_TERMINATOR,0,20)

        SERVINFO = ""
        SERVINFO_list = SERVINFO.split(',')

        SERVINFO = sendAtCmd('AT#SERVINFO',properties.CMD_TERMINATOR,0,2)
        SERVINFO = SERVINFO.replace('"','')
        SERVINFO = SERVINFO.replace(':',',')
        SERVINFO = SERVINFO.replace(' ','')
        SERVINFO_list = SERVINFO.split(',')

        properties.Carrier = SERVINFO_list[4]

        MONI = ""
        MONI_list = MONI.split(' ')

        MONI = sendAtCmd('AT#MONI',properties.CMD_TERMINATOR,0,2)
        MONI = MONI.replace(' ',',')
        MONI = MONI.replace(':',',')
        MONI_list = MONI.split(',')

        properties.CellId = MONI_list[10]

    except:
        printException("getNetworkInfo()")

    return

################################################################################################
## Methods for sending and receiving EMAILS
################################################################################################
    
def sendEMAIL(theEmailSubject,theEmailBody,theTerminator,retry,timeOut):
#This function sends email

  # Input Parameter Definitions
  #   theEmailSubject: The text Email Subject
  #   theEmailBody: The text Email Body
  #   theTerminator: string or character at the end of AT Command
  #   retry:  How many times the command will attempt to retry if not successfully send 
  #   timeOut: number of [1/10 seconds] command could take to respond

    try:

        while (retry != -1):
            print 'AT#SEMAIL="' + EMAIL_ADDRESS + '","' + theEmailSubject + '",0'

            res = MDM.send('AT#SEMAIL="' + EMAIL_ADDRESS + '","' + theEmailSubject + '",0', 0)
            res = MDM.sendbyte(0x0d, 0)
            res = mdmResponse('\r\n>', timeOut)
            print res 

            res = MDM.send(theEmailBody, 0)
            res = MDM.sendbyte(0x1a, 0)

            #Wait for AT command response
            while (1):
                res = mdmResponse(theTerminator, timeOut)
              
                #Did AT command respond without error?    
                pos1 = res.rfind(theTerminator,0,len(res))
                if (pos1 != -1):
                    retry = -1
                    res = parseResponse(res)
                else:
                    retry = retry - 1

    except:
        printException("sendEMAIL()")

    print res
  
    return res

################################################################################################
## Misc support Methods
################################################################################################

def delaySec(seconds):

    try:

        if(seconds<=0): return    

        timerA = timers.timer(0)
        timerA.start(seconds)
        while 1:
            MOD.watchdogReset()
            if timerA.isexpired():
                break

    except:
        printException("delaySec()")

    return

def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> ATC"
    print "METHOD -> " + methodName

    return
