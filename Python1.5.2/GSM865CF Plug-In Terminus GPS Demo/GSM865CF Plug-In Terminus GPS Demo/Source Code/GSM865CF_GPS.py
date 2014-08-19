#GPS Demo for the Terminus Plug-in Terminal
# Janus Model#  GSM865CF V1.1
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
##      GSM865CF_GPS.py
##  REVISION HISTORY:
##      1.0   04/22/2011  TWH --  Init Release
##


import MDM              #code owned by: Telit
import MOD              #code owned by: Telit
import timers           #code owned by: Telit
import sys              #code owned by: Telit

import ATC              #Version V1.2, code owned by: Janus Remote Communications
import NETWORK          #Version V1.1, code owned by: Janus Remote Communications
import GPRS             #Version V1.2, code owned by: Janus Remote Communications
import MS20             #Version V1.0, code owned by: Janus Remote Communications
import DEBUG_CF         #Version V1.0, code owned by: Janus Remote Communications

##------------------------------------------------------------------------------------------------------------------
## NOTES
##  1.)  exceptions.pyo must be loaded on the Telit module in order for this code to work correctly
##
##  2.)  Don't include the following line of code in any of your modules: 'import exceptions'
##
##  3.)  See Main Script, Application Specific Configuration section.  Demo must be altered for customer settings
##
##  4.)  Debug information:
##          a.) You must configure the following COM ports to debug this application in the Pythonwin IDE
##                i.  MDM  --> PC COM port connected to the AT Command Port
##               ii.  SER  --> A free PC COM port, this port will not be connected and is needed because of the import SER in the DEBUG_CF module.
##              iii.  SER2 --> PC COM port connected to the NAVSYN GPS Port
##          b.) When debugging in the IDE debug messages will display via print statements displayed in the "Interactive Window" of Pythonwin IDE
##            
##  5.)  Please read "GSM865CF Plug-in Terminal GPS Demonstration Guide.pdf"
##
##  6.)  Demo requires that the TRACE serial port be connected via NULL MODEM cable to the GPS serial port of the GSM865CF Plug-in Terminal
##------------------------------------------------------------------------------------------------------------------

class myApp:
    IMEI = ''
    BAND = ''
    NETWORK = ''
    APN = ''
    IP = ''
    PORT = ''
    PROTOCOL = ''
    INTERVAL = ''
    RUN_MODE = ''

#Main Script
# ###############################################################
def main():

    try: 

        timerA = timers.timer(0)
        timerA.start(1)

        # Set Global Watchdog timeout in Seconds
        MOD.watchdogEnable(300)

        #Increase CPU speed at cost of increased current consumption
        ATC.sendAtCmd('AT#CPUMODE=1',ATC.properties.CMD_TERMINATOR,0,5)

        #Turn off GSM TX/RX
        ATC.sendAtCmd('AT+CFUN=4',ATC.properties.CMD_TERMINATOR,0,5)

        #Initialize MS20 Receiver
        res = MS20.initGPS('9600','8N1')
        if not(res == 0):
            if (res == -1):
                DEBUG_CF.sendMsg("MS20 Exception occurred\r\n",myApp.RUN_MODE)
            elif (res == -3):
                DEBUG_CF.sendMsg("NMEA Command response Checksum fail\r\n",myApp.RUN_MODE)
            elif (res == -4):
                DEBUG_CF.sendMsg("No NMEA Command response\r\n",myApp.RUN_MODE)
                DEBUG_CF.sendMsg("Is NAVSYNC serial port connected to TRACE port via NULL MODEM cable?\r\n",myApp.RUN_MODE)
                DEBUG_CF.sendMsg("For CF_EVAL_PCB001 V3.1 evaluation boards or newer => SW1, MODE1 = ON\r\n",myApp.RUN_MODE)
                DEBUG_CF.sendMsg("See GSM865CF Plug-in Terminal GPS Demonstration User Guide for more info\r\n",myApp.RUN_MODE)
            elif (res == -5):
                DEBUG_CF.sendMsg("Incorrect NMEA command response\r\n",myApp.RUN_MODE)
            elif (res > 0):
                DEBUG_CF.sendMsg("MS20 Error Number: " + str(res) + "\r\n",myApp.RUN_MODE)            
            else:
                DEBUG_CF.sendMsg("Unknown error\r\n",myApp.RUN_MODE)

            MOD.sleep(40)

            return

        DEBUG_CF.sendMsg("MS20 Initialization Complete\r\n",myApp.RUN_MODE)
        DEBUG_CF.sendMsg("GPS Application Version: " + MS20.GPSdata.APP_VER + "\r\n",myApp.RUN_MODE)
        
        # Wait for GPS module to obtain position data
        DEBUG_CF.sendMsg("Waiting for valid position",myApp.RUN_MODE)
        #Poll NMEA GPGLL Sentence
        if (MS20.pollNMEA('2',5) == 0): exitLoop = MS20.GPSdata.GPGLL.split(',')[6]
        while(exitLoop != 'A'):
            MOD.watchdogReset()
            #Poll NMEA GPGLL Sentence
            if (MS20.pollNMEA('2',5) == 0): exitLoop = MS20.GPSdata.GPGLL.split(',')[6]
            DEBUG_CF.sendMsg(".",myApp.RUN_MODE)

        DEBUG_CF.sendMsg("\r\nPosition acquired: " +str(timerA.count()) + " Seconds (Referenced to script start time)\r\n",myApp.RUN_MODE)

        #Increase CPU speed during TX/RX only
        ATC.sendAtCmd('AT#CPUMODE=2',ATC.properties.CMD_TERMINATOR,0,5)

        #Activate Low Power mode, Turn off GSM TX/RX
        ATC.sendAtCmd('AT+CFUN=5',ATC.properties.CMD_TERMINATOR,0,5)

        #Set Network specific settings
        res = NETWORK.initGsmNetwork(myApp.NETWORK,myApp.BAND)
        if (res == -1):
            return
        DEBUG_CF.sendMsg("Network Initialization Complete\r\n",myApp.RUN_MODE)

        #Wait for GSM Registration
        DEBUG_CF.sendMsg("Waiting for GSM Registration",myApp.RUN_MODE)
        #Check GSM registration
        exitLoop = NETWORK.isGsmRegistered(1)
        while(exitLoop != 0):
            MOD.watchdogReset()
            #Check GSM registration
            exitLoop = NETWORK.isGsmRegistered(1)
            DEBUG_CF.sendMsg(".",myApp.RUN_MODE)

        DEBUG_CF.sendMsg("\r\nTerminal is registered to a GSM network\r\n",myApp.RUN_MODE)

        #Init GPRS
        GPRS.init('1',myApp.APN)
        DEBUG_CF.sendMsg("GPRS Initialization Complete\r\n",myApp.RUN_MODE)

        #Wait for GPRS attach        
        DEBUG_CF.sendMsg("Waiting for GPRS Attach",myApp.RUN_MODE)
        #Check GPRS Attach
        exitLoop = NETWORK.isGprsAttached(1)
        while(exitLoop != 0):
            MOD.watchdogReset()
            #Check GPRS Attach
            exitLoop = NETWORK.isGprsAttached(1)
            DEBUG_CF.sendMsg(".",myApp.RUN_MODE)

        DEBUG_CF.sendMsg("\r\nTerminal is attached to GPRS service\r\n",myApp.RUN_MODE)

        #Record IMEI number        
        myApp.IMEI = ATC.sendAtCmd('AT+CGSN',ATC.properties.CMD_TERMINATOR,0,5)
        DEBUG_CF.sendMsg("IMEI #: " + myApp.IMEI + "\r\n",myApp.RUN_MODE)
        
        # Start timeout timer            
        timerB = timers.timer(0)
        timerB.start(1)
        while(not(timerB.isexpired())): exitCode = -1

        # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
        while (1):
                    
            exitCode = -1
            while (exitCode==-1):

                MOD.watchdogReset()

                #If interval timer expires then send packet to server       
                if (timerB.isexpired()):

                    #Poll NMEA GPGLL Sentence
                    res = MS20.pollNMEA('2',5)
                    DEBUG_CF.sendMsg("Current GPGLL sentence: " + MS20.GPSdata.GPGLL,myApp.RUN_MODE)

                    DEBUG_CF.sendMsg("Opening Connection to server: " + myApp.IP + ":" + myApp.PORT + "\r\n",myApp.RUN_MODE)
                    #Connect to server
                    #Pass in: IP Address, IP Port, sockNum, GPRSuserName, GPRSuserPassword,Command Mode
                    res = GPRS.openSocket(myApp.IP,myApp.PORT,'1','','',myApp.PROTOCOL,'1')

                    try:
                        #If socket open upload data
                        if (res == 'OK'):

                            DEBUG_CF.sendMsg("Connection opened\r\n",myApp.RUN_MODE)

                            #Build String to send to customer server            
                            STR1 = myApp.IMEI +',' + MS20.GPSdata.GPGLL

                            DEBUG_CF.sendMsg("Sending Data: " + STR1,myApp.RUN_MODE)

                            #Send STR1 to server
                            res = GPRS.send_CM(STR1,1,10)                         

                            DEBUG_CF.sendMsg("Data Sent\r\n",myApp.RUN_MODE)
                            
                            #Close Socket
                            res = GPRS.closeSocket('1')

                            DEBUG_CF.sendMsg("Connection Closed\r\n",myApp.RUN_MODE)

                            exitCode = 0
                            
                        else:

                            DEBUG_CF.sendMsg("Connection failed to open\r\n",myApp.RUN_MODE)                            

                            #What is the signal strength?
                            res = ATC.sendAtCmd('AT+CSQ',ATC.properties.CMD_TERMINATOR,0,5)
                            DEBUG_CF.sendMsg("Signal Strength (AT+CSQ): " + res + "\r\n",myApp.RUN_MODE)

                            # Is Terminus still connected to GSM Network?                                                                        
                            res = NETWORK.isGsmRegistered(1)
                            if (res == 0):
                                DEBUG_CF.sendMsg("GSM865CF is registered on GSM network\r\n",myApp.RUN_MODE)
                            else:
                                DEBUG_CF.sendMsg("GSM865CF is NOT registered on GSM network\r\n",myApp.RUN_MODE)
                                
                            #Is a PDP context activated?
                            res = ATC.sendAtCmd('AT#SGACT?',ATC.properties.CMD_TERMINATOR,0,20)
                            DEBUG_CF.sendMsg("PDP Context status (AT#SGACT?): " + res + "\r\n",myApp.RUN_MODE)

                            # Is Terminus still attached to GPRS service?
                            res = NETWORK.isGprsAttached(1)
                            if (res == 0):
                                DEBUG_CF.sendMsg("GSM865CF is attached to GPRS service\r\n",myApp.RUN_MODE)
                            else:
                                DEBUG_CF.sendMsg("GSM865CF is NOT attached to GPRS service\r\n",myApp.RUN_MODE)

                    except:
                        DEBUG_CF.sendMsg("Script encountered an exception while uploading data to server\r\n",myApp.RUN_MODE)
                        DEBUG_CF.sendMsg("Exception Type: " + str(sys.exc_type) + "\r\n",myApp.RUN_MODE)
                        DEBUG_CF.sendMsg("MODULE -> GSM865CF_GPS\r\n",myApp.RUN_MODE)
                        return
                        
                else:
                    DEBUG_CF.CLS(myApp.RUN_MODE)
                    DEBUG_CF.sendMsg("Next update in: " + str(int(myApp.INTERVAL) - timerB.count()) + " Seconds\r\n",myApp.RUN_MODE)
                    MOD.sleep(10)
                    
            ## Re-Start timeout timer            
            timerB = timers.timer(0)
            timerB.start(int(myApp.INTERVAL))

    except:
        DEBUG_CF.sendMsg("Script encountered an exception\r\n",myApp.RUN_MODE)
        DEBUG_CF.sendMsg("Exception Type: " + str(sys.exc_type) + "\r\n",myApp.RUN_MODE)
        DEBUG_CF.sendMsg("MODULE -> GSM865CF_GPS\r\n",myApp.RUN_MODE)
        return


try:
    ##----------------------------------------------------------------------------------------------------- 
    ## Application Specific Configuration 
    ##----------------------------------------------------------------------------------------------------- 

    ## BAND 
    ## Please refer to AT Command guide for AT#BND
    ## If Terminal used in North America (BAND = '3')
    myApp.BAND = '3'

    ## NETWORK 
    ## If Terminal used on ATT / Cingular in North America (NETWORK = 'ATT') 
    ## Else (NETWORK = 'GSM') 
    myApp.NETWORK = 'ATT' 

    ## APN 
    ## Gateway Address for GPRS traffic 
    ## This setting is GSM Provider and possible customer specific when a VPN is used 
    ## This demo is defaulted with proxy that is used for ATT wireless (Blue Network) 
    ## You MUST obtain the APN setting for your GSM account.  Please call GSM provider!
    myApp.APN = 'proxy' 

    ## IP 
    ## IP address of server that will interact with this GPS demonstration.
    ## Address in this example is not operational for customer evaluation.
    ## Customer must have a server setup to interact with this demo.
    myApp.IP = 'xxx.xxx.xxx.xxx'
     
    ## PORT 
    ## PORT number of server that will interact with this GPS demonstration.
    ## PORT number in this example is not operational for customer evaluation.
    ## Customer must have a server setup to interact with this demo.
    myApp.PORT = '5556'
     
    ## PROTOCOL
    ## If using TCPIP (PROTOCOL = 'TCPIP')
    ## Else leave blank (PROTOCOL = '')
    myApp.PROTOCOL = 'TCPIP'

    ## INTERVAL
    ## How many seconds the demo will wait before sending new GPS data to server.
    ## In this demo, GPS data will be sent every 60 seconds (INTERVAL = '60')
    myApp.INTERVAL = '60' 

    try:
        myApp.RUN_MODE = 0              #Running in IDE
        test = float(myApp.RUN_MODE)    #float not implemented in Telit module
    except:
        myApp.RUN_MODE = 1              #Running in GE865-DUAL Python Environment

    DEBUG_CF.init('115200','8N1')
    DEBUG_CF.CLS(myApp.RUN_MODE)
    DEBUG_CF.sendMsg("GSM865CF GPS DEMO\r\r\n",myApp.RUN_MODE)

    main()
    
    DEBUG_CF.sendMsg("Main Script Exit",myApp.RUN_MODE)
    DEBUG_CF.sendMsg("....Rebooting",myApp.RUN_MODE)
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot()

except:

    DEBUG_CF.sendMsg("Main Script encountered an exception",myApp.RUN_MODE)
    DEBUG_CF.sendMsg("Exception Type: " + str(sys.exc_type),myApp.RUN_MODE)
    DEBUG_CF.sendMsg("MODULE -> GSM865CF_GPS",myApp.RUN_MODE)
    DEBUG_CF.sendMsg("....Rebooting",myApp.RUN_MODE)
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot()
