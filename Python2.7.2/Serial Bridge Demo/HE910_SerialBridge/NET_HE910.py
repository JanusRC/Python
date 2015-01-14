##--------------------------------------------------------------------------------------
## Module: NET_HE910.py
## Release Information:
##  V1.0.0    (Thomas W. Heck, 09/24/2012)   :   Initial release
##--------------------------------------------------------------------------------------

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

import ATC_HE910 as myATC

class properties:
    Carrier = ''
    CellId = ''

def isRegistered(timeOut):
# This function waits until the cellular module is registered to a Network

    rtnList = [-1,-1]    #[return status,return data, exception]
    # return status:
    #   -2:    Timeout
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:

        #Start timeout counter 
        start = time.time()   

        #Wait until registered to Network
        while True:

            rtnList = myATC.sendAtCmd('AT+CREG?',myATC.properties.CMD_TERMINATOR,5)

            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            elif rtnList[0] == 1: #CREG responded without errors
                if (rtnList[1][rtnList[1].rfind(',')+1:len(rtnList[1])] == '5' or rtnList[1][rtnList[1].rfind(',')+1:len(rtnList[1])] == '1'):
                    rtnList[0] = 0 #Successful registration, no data returned
                    break
                if (time.time() - start) > timeOut:
                    rtnList[0] = -2 #Timeout waiting for registration
                    break
                time.sleep(1)

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def isDataAttached(CGMM, timeOut):
# This function waits until module attaches to data service

    rtnList = [-1,-1]    #[return status,return data, exception]
    # return status:
    #   -2:    Timeout
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    if (CGMM != "GE865") or (CGMM != "HE910"):
        rtnList[0] = 0
        return rtnList

    try:

        #Start timeout counter 
        start = time.time()  
        
        #Wait until attached to GPRS service
        while True:

            rtnList = myATC.sendAtCmd('AT+CGREG?',myATC.properties.CMD_TERMINATOR,5)

            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            elif rtnList[0] == 1: #CGREG responded without errors
                if (rtnList[1][rtnList[1].rfind(',')+1:len(rtnList[1])] == '5' or rtnList[1][rtnList[1].rfind(',')+1:len(rtnList[1])] == '1'):
                    rtnList[0] = 0 #Successful registration, no data returned
                    break
                if (time.time() - start) > timeOut:
                    rtnList[0] = -2 #Timeout waiting for registration
                    break
                time.sleep(1)

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def initNetwork(ENS):
# This function sets all Network specific settings
    # Input Parameter Definitions
    #   inSTR1:    Cellular device model
    #   inSTR2:    AT#ENS, range(0:1)

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    reboot_needed = False

    try:

        rtnList = wait4SIMReady()        

        rtnList = myATC.sendAtCmd("AT#SELINT?",myATC.properties.CMD_TERMINATOR,2)                   #query SELINT setting
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList[0] == 1:
            if (rtnList[1] != "#SELINT: 2"):
                rtnList = myATC.sendAtCmd('AT#SELINT=2',myATC.properties.CMD_TERMINATOR,2)          #use of most recent AT command set
                if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
                reboot_needed = True

        if (ENS == "1"):

            #Set module to work on US ATT Network  
            rtnList = myATC.sendAtCmd("AT#ENS?",myATC.properties.CMD_TERMINATOR,2)                  #query ENS setting
            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            elif rtnList[0] == 1: 
                if (rtnList[1] != "#ENS: 1"):
                    rtnList = myATC.sendAtCmd('AT#ENS=1',myATC.properties.CMD_TERMINATOR,2)         #sets all ATT requirements
                    if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
                    reboot_needed = True

        else:

            #Set module to work on US GSM Networks  
            rtnList = myATC.sendAtCmd("AT#ENS?",myATC.properties.CMD_TERMINATOR,2)                  #query ENS setting
            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            elif rtnList[0] == 1: 
                if (rtnList[1] != "#ENS: 0"):
                    rtnList = myATC.sendAtCmd('AT#ENS=0',myATC.properties.CMD_TERMINATOR,2)         #sets all ATT requirements
                    if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
                    reboot_needed = True

            rtnList = myATC.sendAtCmd('AT#AUTOBND?',myATC.properties.CMD_TERMINATOR,2)              #query AUTOBND setting
            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            elif rtnList[0] == 1: 
                if (rtnList[1] != "#AUTOBND: 2"):
                    rtnList = myATC.sendAtCmd('AT#AUTOBND=2',myATC.properties.CMD_TERMINATOR,2)     #enable Quad band system selection
                    if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
                    reboot_needed = True

        if (reboot_needed):
            rtnList = reboot()

        rtnList[0] = 0

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def getNetworkTime(timeOut):
# This function forces the Network to update RTC with GSM Network Time

    rtnList = [-1,-1]    #[return status,return data, exception]
    # return status:
    #   -2:    Timeout
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:

        rtnList = myATC.sendAtCmd("AT#NITZ=1",myATC.properties.CMD_TERMINATOR,2)               #set NITZ command to update Network Time
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList 
        
        rtnList = myATC.sendAtCmd("AT+COPS=2",myATC.properties.CMD_TERMINATOR,2)               #set COPS command to force GSM Registration to disconnect      
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList 
        
        #Start timeout counter 
        start = time.time()  
        
        #Wait until GSM module is not registered to Network
        while (1):
            #MOD.watchdogrtnListet()
            rtnList = myATC.sendAtCmd('AT+CREG?',myATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList 
            elif rtnList[0] == 1:
                if (rtnList[1] == "+CREG: 0,0"):
                    break
                if (time.time() - start) > timeOut:
                    rtnList[0] = -2
                    return rtnList

        rtnList = myATC.sendAtCmd("AT+COPS=0",myATC.properties.CMD_TERMINATOR,2)               #set COPS command to force GSM Registration     
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        
        rtnList = isRegistered(timeOut)
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList[0] == 0:
            rtnList[0] = 0
        elif rtnList[0] == -2:
            #Timeout occurred
            rtnList[0] = -2

        rtnList = myATC.sendAtCmd("AT+CCLK?",myATC.properties.CMD_TERMINATOR,2)               #Query RTC Clock
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def wait4SIMReady():

    #SIM status control - to avoid the 'sim busy' error
    # The following sequence loops forever until SIM card is ready for use

    rtnList = [-1,-1]    #[return status,return data, exception]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:

        print 'SIM Verification Cycle' + "\r\n"
        rtnList = myATC.sendAtCmd('AT+CPIN?' ,myATC.properties.CMD_TERMINATOR,5)
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList [0] == 1:
            if rtnList [1].find("READY") < 0:
                print 'SIM busy! Please wait!' + "\r\n"

        while rtnList[1].find("READY") < 0 :
            rtnList = myATC.sendAtCmd('AT+CPIN?' ,myATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
            time.sleep(2)

        print 'SIM Ready' + "\r\n"

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def getNetworkInfo():

    rtnList = [-1,-1]    #[return status,return data, exception]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:

        rtnList = myATC.sendAtCmd('AT#SERVINFO',myATC.properties.CMD_TERMINATOR,2)
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList [0] == 1:
            rtnList[1] = rtnList[1].replace('"','')
            rtnList[1] = rtnList[1].replace(':',',')
            rtnList[1] = rtnList[1].replace(' ','')
            SERVINFO_list = rtnList[1].split(',')

            properties.Carrier = SERVINFO_list[4]

        rtnList = myATC.sendAtCmd('AT#MONI',myATC.properties.CMD_TERMINATOR,2)
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        elif rtnList [0] == 1:
            rtnList[1] = rtnList[1].replace(' ',',')
            rtnList[1] = rtnList[1].replace(':',',')
            MONI_list = rtnList[1].split(',')

            properties.CellId = MONI_list[10]

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def reboot():
    
    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data
    
    try:    

        rtnList = myATC.sendAtCmd('AT&P0',myATC.properties.CMD_TERMINATOR,2)                #Save Profile
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        rtnList = myATC.sendAtCmd('AT&W0',myATC.properties.CMD_TERMINATOR,2)                #Save Settings
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        time.sleep(1)
        rtnList = myATC.sendAtCmd('AT#reboot',myATC.properties.CMD_TERMINATOR,2)            #Reboot Telit Module
        if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
        time.sleep(1)
        
        rtnList = wait4SIMReady()

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList
