##------------------------------------------------------------------------------------------------------------------
## Module: ATC_HE910.py
## Release Information:
##  V1.0.0    (Thomas W. Heck, 09/24/2012)   :   Initial release
##------------------------------------------------------------------------------------------------------------------

##--------------------------------------------------------------------------------------
## NOTES
##  1.)  Works with the HE910 module 
##--------------------------------------------------------------------------------------

#
#Copyright 2012, Janus Remote Communications
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

import time
import sys

import MDM as mySER

class properties:
    IMEI = ''
    SIM = ''
    CMD_TERMINATOR = 'OK\r\n'    # This is the standard string termination of a AT command response
    firmwareMajor = ''
    firmwareMinor = ''
    firmwareRevision = ''
    firmwareModel = ''

################################################################################################
## Methods for sending and receiving AT Commands
################################################################################################
def sendAtCmd(theCommand, theTerminator, timeOut):
# This function sends an AT command to the MDM interface

    # Input Parameter Definitions
    #   theCommand: The AT command to send to MDM interface
    #   theTerminator: string or character at the end of AT Command 
    #   timeOut: number of seconds command could take to respond

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data


        #Clear input buffer
        rtnList[1] = 'junk'
        while(rtnList[1] != ''):
            rtnList[1] = mySER.read()

        print 'Sending AT Command: ' + theCommand + "\r\n"
        rtnList[1] = mySER.send(theCommand,2)
        rtnList[1] = mySER.sendbyte(0x0d,2)

        while True:
            #Wait for AT command response
            rtnList = mdmResponse(theTerminator, timeOut)
            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            elif rtnList[0] == 1:
                #what happens if res doesn't return data?
                #Did AT command respond without error?
                pos1 = rtnList[1].rfind('ERROR',0,len(rtnList[1]))    
                pos2 = rtnList[1].rfind(theTerminator,0,len(rtnList[1]))
                if ((pos1 != -1) or (pos2 != -1)) :
                    rtnList = parseResponse(rtnList[1])
                    if rtnList[0] == -1: return rtnList
                    elif rtnList[0] == 1:
                        #what happens if res doesn't return data?
                        rtnList[0] = 1
                        break

    except:
        print sys.exc_info()
        rtnList[0] = -1

    print rtnList[1]

    return rtnList

def mdmResponse(theTerminator, timeOut):
# This function waits for AT Command response and handles errors and ignores unsolicited responses

# Input Parameter Definitions
#   theTerminator: string or character at the end of a received string which indicates end of a response
#   timeOut: number of seconds command could take to respond

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data

        print 'Waiting for AT Command Response' + "\r\n"

        #Start timeout counter 
        start = time.time()       

        #Wait for response
        rtnList[1] = ''
        while ((rtnList[1].find(theTerminator)<=-1) and (rtnList[1].find("ERROR")<=-1)):
            #MOD.watchdogReset()
            rtnList[1] += mySER.read()

            pass            
            if (time.time() - start) > timeOut:
                rtnList[0] = -2
                print "AT command timed out" + "\r\n"
                return rtnList
                        
        rtnList[0] = 1

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def parseResponse(inSTR):
# This function parses out data return from AT commands

    # Input Parameter Definitions
    #   inSTR:  The response string from and AT command

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:

        rtnList[1] = ''
        lenght = len(inSTR)

        if lenght != 0:
            pos1 = inSTR.find('ERROR',0,lenght)
            if (pos1 != -1):
                rtnList[1] = 'ERROR'
            else:
                list_in = inSTR.split( '\r\n' )
                rtnList[1] = list_in[ 1 ]

        if len(rtnList[1]) > 0:
            rtnList[0] = 1

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

################################################################################################
## Misc. Methods for GSM Modules
################################################################################################

def reboot():
# This method does return a response.  After the AT#REBOOT command executes the GSM module will
# reset and the script will restart depending on the #STARTMODESCR settings.

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data

        time.sleep(1.5)  #required to halt Python thread and allow NVM Flash to update
        print "Rebooting Modem!" + "\r\n"
        rtnList = sendAtCmd('AT#REBOOT',properties.CMD_TERMINATOR,20)            

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def getFirmwareRev():

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:
        rtnList = sendAtCmd("AT+CGMR",properties.CMD_TERMINATOR,2)                #query firmware revision
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList[0] == 1:

            parts = rtnList[1].split(".")

            properties.firmwareMajor = parts[0]
            properties.firmwareMinor = parts[1]
            properties.firmwareRevision = parts[2][2]
            properties.firmwareModel = parts[2][0] + parts[2][1]            

            rtnList[0] = 0

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def getUnitInfo():

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:
        rtnList = sendAtCmd('AT+CIMI',properties.CMD_TERMINATOR,5)                #query IMSI (Phone Number)
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList[0] == 1: properties.SIM = rtnList[1]

        rtnList = sendAtCmd('AT+CGSN',properties.CMD_TERMINATOR,5)                #query SIM IMEI
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList[0] == 1: properties.IMEI = rtnList[1]          

        rtnList[0] = 0

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList
