#Copyright © 2010, Janus Remote Communications
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


## GSM Network Functions
## Written By Thomas W. Heck
##  MODULE:
##      NETWORK.py
##  REVISION HISTORY:
##      1.0.0   04/24/2009  TWH --  Init Release
##      1.0.1   05/07/2010  TWH --  1.) Changed NETWORK.initGsmNetwork() to set AT#STIA=1,10 without
##                                      checking previous state.
##      1.0.2   05/19/2010  TWH --  1.) Added properties.Carrier & CellId
##                                  2.) Added method getNetworkInfo()
##                                  3.) Updated initGsmNetwork() ti include provisions for 10.00.xxx firmware

import MOD              #code owned by: Telit
import timers           #code owned by: Telit
import sys              #code owned by: Telit

import ATC              #code owned by: Janus Remote Communications

class properties:
    Carrier = ''
    CellId = ''

def isGsmRegistered(timeOut):
# This function waits until the GSM module is registered to a GSM Network

    exitLoop = -1

    try:

        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(timeOut)
        
        #Wait until registered to GSM Network
        while (exitLoop == -1):
            MOD.watchdogReset()
            res = ATC.sendAtCmd('AT+CREG?',ATC.properties.CMD_TERMINATOR,0,5)
            if (res[res.rfind(',')+1:len(res)] == '5' or res[res.rfind(',')+1:len(res)] == '1'):
                exitLoop = 0
                break
            if timerA.isexpired():
                break #Exit while
            
    except:

        printException("isGsmRegistered()")

    return exitLoop

def isGprsAttached(timeOut):
# This function waits until the GPRS attaches

    exitLoop = -1

    try:

        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(timeOut)
        
        #Wait until registered to GSM Network
        while (exitLoop == -1):
            MOD.watchdogReset()
            res = ATC.sendAtCmd('AT+CGREG?',ATC.properties.CMD_TERMINATOR,0,5)
            if (res[res.rfind(',')+1:len(res)] == '5' or res[res.rfind(',')+1:len(res)] == '1'):
                exitLoop = 0
                break
            if timerA.isexpired():
                break #Exit while
            
    except:

        printException("isGprsAttached()")

    return exitLoop

def initGsmNetwork(inSTR1, inSTR2):
# This function sets all Network specific settings
    # Input Parameter Definitions
    #   inSTR1:     GSM Network (ATT or GSM)
    #   inSTR2:     AT#BND=inSTR2 (0,1,2,or 3)

    tmpReturn = -1

    try:

        #res = ATC.sendAtCmd("AT+CFUN=1",ATC.properties.CMD_TERMINATOR,0,2)                  #Set Automatic Operator Selection        

        res = ATC.getUnitInfo()
        if (res == -1):
            return tmpReturn

        res = ATC.sendAtCmd("AT#SELINT?",ATC.properties.CMD_TERMINATOR,0,2)                 #query SELINT setting
        if (res != "#SELINT: 2"):
            res = ATC.sendAtCmd('AT#SELINT=2',ATC.properties.CMD_TERMINATOR,0,2)            #use of most recent AT command set
            res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)                  #Save Profile
            res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)                  #Save Settings
            return tmpReturn

        if (ATC.properties.firmwareMajor == '10'):

            #Firmware specific settings                
            if (ATC.properties.firmwareMinor == '00'):
                res = ATC.sendAtCmd('AT#AUTOBND?',ATC.properties.CMD_TERMINATOR,3,2)	        #query AUTOBND setting
                if (res != "#AUTOBND: 1"):
                    res = ATC.sendAtCmd('AT#AUTOBND=1',ATC.properties.CMD_TERMINATOR,3,2)	    #enable Quad band system selection
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn
                
            else:                                                                               #No other firmware releases yet
                res = ATC.sendAtCmd('AT#AUTOBND?',ATC.properties.CMD_TERMINATOR,3,2)	        #query AUTOBND setting
                if (res != "#AUTOBND: 2"):
                    res = ATC.sendAtCmd('AT#AUTOBND=2',ATC.properties.CMD_TERMINATOR,3,2)	    #enable instant Quad band system selection
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn
            
            #Apply Network Specific settings see myApp.xxxx assignment above
            if (inSTR1 == "ATT"):
                #Set module to work on US ATT Network  
                res = ATC.sendAtCmd("AT#ENS?",ATC.properties.CMD_TERMINATOR,0,2)                #query ENS setting
                if (res != "#ENS: 1"):
                    res = ATC.sendAtCmd('AT#ENS=1',ATC.properties.CMD_TERMINATOR,0,2)           #sets all ATT requirements
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn


            else:
                #Set module to work on all other Networks
                res = ATC.sendAtCmd('AT#ENS?',ATC.properties.CMD_TERMINATOR,0,2) 
                if (res != "#ENS: 0"):
                    res = ATC.sendAtCmd('AT#ENS=0',ATC.properties.CMD_TERMINATOR,0,2)           #disable all ATT requirements
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn
                
                res = ATC.sendAtCmd("AT#BND?",ATC.properties.CMD_TERMINATOR,0,2)                #query BND setting
                if (res != "#BND: " + inSTR2):
                    res = ATC.sendAtCmd('AT#BND='+ inSTR2,ATC.properties.CMD_TERMINATOR,3,2)    #set bands to 850/1900 
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn


                res = ATC.sendAtCmd("AT#PLMNMODE?",ATC.properties.CMD_TERMINATOR,0,2)           #query PLMN setting
                if (res != "#PLMNMODE: 1"):
                    res = ATC.sendAtCmd('AT#PLMNMODE=1',ATC.properties.CMD_TERMINATOR,0,2)      #enable operator name updating
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn

                res = wait4SIMReady()                                                           #wait for SIM to be ready for use
                res = ATC.sendAtCmd("AT#STIA?",ATC.properties.CMD_TERMINATOR,0,2)               #query STIA settings
                if ((res.find('STIA: 0,1')==-1) and (res.find('STIA: 1,1')==-1)):
                    res = ATC.sendAtCmd('AT#STIA=1,10',ATC.properties.CMD_TERMINATOR,0,2)       #enable SAT - SIM Application Tool-Kit                
                    res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                    res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                    return tmpReturn
            
        elif (ATC.properties.firmwareMajor == '10'):

                if (inSTR1 == "ATT"):

                    #Set module to work on US ATT Network  
                    res = ATC.sendAtCmd("AT#ENS?",ATC.properties.CMD_TERMINATOR,0,2)                #query ENS setting
                    if (res != "#ENS: 1"):
                        res = ATC.sendAtCmd('AT#ENS=1',ATC.properties.CMD_TERMINATOR,0,2)           #sets all ATT requirements
                        res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                        res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                        return tmpReturn
                                            
                else:
                    
                    res = ATC.sendAtCmd('AT#AUTOBND?',ATC.properties.CMD_TERMINATOR,3,2)	        #query AUTOBND setting
                    if (res != "#AUTOBND: 2"):
                        res = ATC.sendAtCmd('AT#AUTOBND=2',ATC.properties.CMD_TERMINATOR,3,2)	    #enable Quad band system selection
                        res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                        res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                        return tmpReturn

                    res = ATC.sendAtCmd("AT#PLMNMODE?",ATC.properties.CMD_TERMINATOR,0,2)           #query PLMN setting
                    if (res != "#PLMNMODE: 1"):
                        res = ATC.sendAtCmd('AT#PLMNMODE=1',ATC.properties.CMD_TERMINATOR,0,2)      #enable operator name updating
                        res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                        res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                        return tmpReturn

                    res = wait4SIMReady()                                                           #wait for SIM to be ready for use
                    res = ATC.sendAtCmd("AT#STIA?",ATC.properties.CMD_TERMINATOR,0,2)               #query STIA settings
                    if ((res.find('STIA: 0,1')==-1) and (res.find('STIA: 1,1')==-1)):
                        res = ATC.sendAtCmd('AT#STIA=1,10',ATC.properties.CMD_TERMINATOR,0,2)       #enable SAT - SIM Application Tool-Kit                
                        res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
                        res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings
                        return tmpReturn



        else:

            print 'Unknown Firmware'                

        tmpReturn = 0
        
    except:
        printException("initGsmNetwork(" + myNetwork + ")")

    return tmpReturn

def getNetworkTime(timeOut):
# This function forces the Network to update RTC with GSM Network Time

    tmpReturn = -1

    try:

        res = ATC.sendAtCmd("AT#NITZ=1",ATC.properties.CMD_TERMINATOR,0,2)               #set NITZ command to update Network Time

        res = ATC.sendAtCmd("AT+COPS=2",ATC.properties.CMD_TERMINATOR,0,2)               #set COPS command to force GSM Registration to disconnect      

        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(timeOut)
        
        #Wait until GSM module is not registered to Network
        while (1):
            MOD.watchdogReset()
            res = ATC.sendAtCmd('AT+CREG?',ATC.properties.CMD_TERMINATOR,0,5)
            if (res == "+CREG: 0,0"):
                break
            if timerA.isexpired():
                return tmpReturn

        res = ATC.sendAtCmd("AT+COPS=0",ATC.properties.CMD_TERMINATOR,0,2)               #set COPS command to force GSM Registration     

        res = isGsmRegistered(timeOut)
        if (res == 0):
            tmpReturn = 0

        res = ATC.sendAtCmd("AT+CCLK?",ATC.properties.CMD_TERMINATOR,0,2)               #Query RTC Clock
              
    except:
        printException("getNetworkTime")

    return tmpReturn

def wait4SIMReady():

    #SIM status control - to avoid the 'sim busy' error
    # The following sequence loops forever until SIM card is ready for use

    try:

        res = ATC.sendAtCmd("AT#SIMDET?",ATC.properties.CMD_TERMINATOR,0,2)             #query Sim detection style
        if (res.find("#SIMDET: 2")< 0):
            res = ATC.sendAtCmd('AT#SIMDET=2',ATC.properties.CMD_TERMINATOR,0,2)        #Ensure detection is automatic via SIMIN and not forced
            res = ATC.sendAtCmd('AT&P0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Profile
            res = ATC.sendAtCmd('AT&W0',ATC.properties.CMD_TERMINATOR,0,2)              #Save Settings        

        print 'SIM Verification Cycle'
        SIM_status = ATC.sendAtCmd('AT+CPBS?' ,ATC.properties.CMD_TERMINATOR,0,5)       #We aren't using AT+CPIN? because there are too many possible answers
                                                                                        #This lets us know that the SIM is at least inserted
        if SIM_status.find("+CPBS")<0:
            print 'SIM busy! Please wait!\n'

        while SIM_status.find("+CPBS:")< 0 :
            SIM_status = ATC.sendAtCmd('AT+CPBS?' ,ATC.properties.CMD_TERMINATOR,0,5)
            MOD.sleep(2)
        print 'SIM Ready'

    except:
        printException("wait4SIMReady()")

    return
def getNetworkInfo():

    try:

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

def printException(methodName):
    print("Script encountered an exception.")
    print("Exception Type: " + str(sys.exc_type))
    print("MODULE -> NETWORK")
    print("METHOD -> " + methodName)

    return    