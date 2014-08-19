#Demo HSPA910 SMS Query Program for the T2
# Janus Model#  HSPA910T2
#
#Copyright © 2013, Janus Remote Communications
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


import MDM
import GPS
import time            
import sys                        

import conf
import ATC_HE910 as ATC
import IO_HE910 as myIO
import SER_HE910 as mySER
import NET_HE910 as NETWORK        
import SOCKET_HE910 as SOCKET                  
import SMS_HE910 as mySMS

##------------------------------------------------------------------------------------------------------------------
## Release Information:
##  V1.0    (Clayton W. Knight, )   :   Initial release

##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## NOTES
##  1.)  exceptions.pyo must be loaded on the Telit module in order for this code to work correctly
##  2.)  Don't include the following line of code in any of your modules: 'import exceptions'
##  3.)  See Main Script, Application Specific Configuration section.  Demo must be altered for customer settings
##  4.)  print statements are displayed when using the IDE to debug application
##  5.)  Do not import SER2, GPS in command mode utilizes this interface
##------------------------------------------------------------------------------------------------------------------


def main():

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        #    2:    Error occurred        

        #Initialize the serial interface @ 115200, we must do this or nothing comes out the serial port
        rtnList = mySER.init("115200",'8N1')
        if (rtnList[0] == -1):
            return


        mySER.sendUART("Beginning the T2 SMS Query Program. \r\n\r\n")        
        # Set Global Watchdog timeout in Seconds
        #MOD.watchdogEnable(300)


        #Get configuration from demoT2.conf file, transpose into new local myApp class
        myApp = conf.conf('/sys','demoT2.conf') 
        if myApp.CONF_STATUS != 0:
            mySER.sendUART("DemoT2 configuration error: " + str(myApp.CONF_STATUS)) 
            return rtnList        


        
        mySER.sendUART("Configuration Loaded.\r\n")        

        rtnList = myIO.init()
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning
                
        mySER.sendUART("\r\nInitializing Network Setup. \r\n")
        #Set Network specific settings, wait for SIM card to be ready
        rtnList = NETWORK.initNetwork(myApp.ENS)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

        #Initialize SOCKET communications
        rtnList = SOCKET.init('1',myApp.APN)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning


        mySER.sendUART("Network Setup Initialized. \r\n\r\n")
        
        mySER.sendUART("Initializing GPS \r\n")

        #Turn the GPS ON
        rtnList[1] = GPS.getPowerOnOff()
        while (rtnList[1] != 1):
            GPS.powerOnOff(1)
            rtnList[1] = GPS.getPowerOnOff()
            mySER.sendUART("GPS Status: " + str(rtnList[1]) + "\r\n") 
           

        mySER.sendUART("GPS Initialized. \r\n\r\n")

        mySER.sendUART("Initializing SMS. \r\n")
        
        #Setup SMS
        rtnList = mySMS.configSMS()
        if (rtnList[0] == 0):
            mySER.sendUART("SMS Initialized. \r\n\r\n")
        else:
            return

        #Update Unit information
        rtnList = ATC.getUnitInfo()
        if (rtnList[0] == -1) or rtnList[1] == "ERROR": raise UserWarning     

        # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
        while (1):
            
            #MOD.watchdogReset()

            RegCheck = 0 #Initialize check
            
            mySER.sendUART("Checking Modem Registration. \r\n")
            #Wait until module is registered to GSM Network
            rtnList = NETWORK.isRegistered(180)  #Wait 180 seconds for module to obtain GSM registration
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

            if (rtnList[0] == 0):
                RegCheck = 1
                mySER.sendUART("Modem Registered. Waiting for SMS. \r\n\r\n")
                
            # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
            while (RegCheck == 1):

                #MOD.watchdogReset()

                #Update NMEA Data
                #The following are available through the included GPS module:
                #GPS.getActualPosition(), returns all fields like AT$GPSACP would
                #GPS.getLastGGA()
                #GPS.getLastGLL()
                #GPS.getLastGSA()
                #GPS.getLastGSV()
                #GPS.getLastRMC()
                #GPS.getLastVTG()
                #GPS.getPosition(), this gives LAT/LONG in numeric format

                #For the purposes of this demo, RMC will be used
                #The returned value gives a \r\n at the end so we must strip it for proper usage.
                
                #sleep for 1 second to let the GPS catch up otherwise we eventually get a response that .rstrip errors on
                time.sleep(1)
                
                GPSPositionTemp = ''
                GPSPositionTemp = GPS.getLastRMC()
                GPSPositionTemp = GPSPositionTemp.rstrip()
                   
                rtnList = mySMS.CheckNewSMS()
                #If a new SMS is found and is valid, pass it to the command logic
                if (rtnList[0] == 1):
                    #We have received a new SMS, let's find what it wants us to do.
                    mySER.sendUART("SMS Received.\r\n")
                    mySER.sendUART("SMS Data : " + str(rtnList[1]) + "\r\n")
                    rtnList = mySMS.SMSCommand(rtnList[1])
                    #    0: Pass, action carried out and SMS sent back
                    #   -1: Exception
                    #   -2: Pass, Unrecognized change command or AT command received though
                    #   -3: Unrecognized SMS
                    #   -4: Error sending an SMS to the originating P/N
                    
                    if (rtnList[0] == -1):
                        return


                rtnList = NETWORK.isRegistered(10)  #Check Registration on the fly
                if (rtnList[0] == -1) or (rtnList[0] == -2):
                    RegCheck = 0
                    
                    mySER.sendUART("\r\nRegistration not available, checking status.\r\n")

                    #What is the signal strength?
                    rtnList = ATC.sendAtCmd('AT+CSQ',ATC.properties.CMD_TERMINATOR,0,5)
                    mySER.sendUART("Signal Strength (AT+CSQ): " + rtnList[1]  + "\r\n")

                    #Still registered?
                    rtnList = ATC.sendAtCmd('AT+CREG?',ATC.properties.CMD_TERMINATOR,0,5)
                    mySER.sendUART("Registration Check (AT+CREG?): " + rtnList[1] + "\r\n")

                    break
                
    except UserWarning:
        print 'Controlled Script exit'

    except:
        print sys.exc_info()
        rtnList[0] = -1
        
    return


##--------------------------------------------------------------------------------------------------------------------
## Main Function
##--------------------------------------------------------------------------------------------------------------------

try:

    main()
    print "Main Script Exit"
    
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot()

except:

    print "Main Script encountered an exception"
    print sys.exc_info()
    
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot() 