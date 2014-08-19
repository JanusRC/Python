#Serial 2 GPRS Bridge Demo for the Terminus Terminal
# Janus Model#  GSM865CF
#
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

import MOD              #code owned by: Telit
import MDM              #code owned by: Telit
import timers           #code owned by: Telit
import sys              #code owned by: Telit

import ATC              #code owned by: Janus Remote Communications
import JANUS_SER        #code owned by: Janus Remote Communications
import NETWORK          #code owned by: Janus Remote Communications
import GPRS             #code owned by: Janus Remote Communications

##------------------------------------------------------------------------------------------------------------------
## Release Information:
##  V2.0    (Thomas W. Heck, 05/18/2010)   :   Initial release

##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## NOTES
##  1.)  exceptions.pyo must be loaded on the Telit module in order for this code to work correctly
##  2.)  Don't include the following line of code in any of your modules: 'import exceptions'
##  3.)  See Main Script, Application Specific Configuration section.  Demo must be altered for customer settings
##  4.)  print statements are displayed when using the IDE to debug application
##  5.)  Please read "Terminus Demo Guide - Serial to GPRS Bridge.pdf"
##------------------------------------------------------------------------------------------------------------------

class myApp:
    BAND = ''
    NETWORK = ''
    APN = ''
    IP = ''
    PORT = ''
    PROTOCOL = ''
    USERNAME = ''
    PASSWORD = ''

def main():

    try: 

        # Set Global Watchdog timeout in Seconds
        MOD.watchdogEnable(300)

        res = JANUS_SER.init("115200",'8N1')
        if (res == -1):
            return
  
        #Set Network specific settings
        res = NETWORK.initGsmNetwork(myApp.NETWORK,myApp.BAND)
        if (res == -1):
            return

        #Init GPRS
        GPRS.init('1',myApp.APN)

        #Inform Application that a Data Connection is not available
        JANUS_SER.set_DCD(0)

        # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
        while (1):

            MOD.watchdogReset()

            #Wait until module is registered to GSM Network
            res = NETWORK.isGsmRegistered(180)  #Wait 180 seconds for module to obtain GSM registration
            if (res == -1):
                return
            
            #Wait until module is attached to GPRS    
            res = NETWORK.isGprsAttached(180)  #Wait 180 seconds for module to obtain GPRS Attachment
            if (res == -1):
                return

            #############################################################################################################################
            ## Opening Socket Connection to Server
            #############################################################################################################################

            res = GPRS.openSocket(myApp.IP,myApp.PORT,1,myApp.USERNAME,myApp.PASSWORD,myApp.PROTOCOL,0)

            #Inform Application that a Data Connection is not available
            DCD = MDM.getDCD()
            if (DCD == 1):
                JANUS_SER.set_DCD(1)
                #Forward CONNECT Message to Serial Port
                JANUS_SER.sendUART('\r\nCONNECT\r\n') 

            ##Loop while Socket connected
            while(1):

                MOD.watchdogReset()

                #Forward serial port data to socket connection
                DCD = MDM.getDCD()
                if (DCD == 1):
                    #Get data from serial port
                    res = JANUS_SER.readUART()
                    if (len(res)!=0):
                        #Forward data to open socket
                        res = MDM.send(res,1)

                #Forward  socket data to serial port
                DCD = MDM.getDCD()
                if (DCD == 1):
                    #Get data from open socket connection
                    res = MDM.receive(1)
                    if (len(res)!=0):
                        #Forward socket data to serial port
                        JANUS_SER.sendUART(res) 

                #When socket is closed exit loop via this path
                #Will guarantee that '\r\nNO CARRIER\r\n' is sent every time
                DCD = MDM.getDCD()
                if (DCD == 0):
                    #Inform Application that a Data Connection is not available
                    JANUS_SER.set_DCD(0)
                    ATC.delaySec(1)
                    #Get any remaining data from closed socket connection
                    res = MDM.receive(1)
                    if (len(res)!=0):
                        #Forward socket data to serial port
                        JANUS_SER.sendUART(res)
                    break
    except:
        print "Script encountered an exception"
        print "Exception Type: " + str(sys.exc_type)
        print "MODULE -> TerminusS2E"
        
    return

##--------------------------------------------------------------------------------------------------------------------
## Application Specific Configuration
##--------------------------------------------------------------------------------------------------------------------

## BAND
## Please refer to AT Command guide for AT#BND
## If Terminal used in North America (BAND = '3')
myApp.BAND = '3'

## NETWORK
## If Terminal used on ATT / Cingular in North America (NETWORK = 'ATT')
## Else (NETWORK = 'GSM')
myApp.NETWORK = 'GSM'

## APN
## Gateway Address for GPRS traffic
## This setting is GSM Provider and possible customer specific when a VPN is used
## This demo is defaulted with 'internet' that is used for ATT wireless settings from pre-Cingular days
## You MUST obtain the APN setting for your GSM account.  Please call GSM provider!  Janus can't help you with this.
myApp.APN = 'YOUR NETWORKS APN'

## IP
## IP address of server on the Internet which Terminus will connect to send and receive data
## Address in this example is not operational for customer evaluation.  Customer must have their own server
## setup to interact with this demo.
## IP = 'xxx.xxx.xxx.xxx'
myApp.IP = 'YOUR SERVERS IP ADDRESS'

## PORT
## PORT number of server on the Internet which Terminus will connect to send and receive data
## PORT number in this example is not operational for customer evaluation.  Customer must have their own server
## setup to interact with this demo.
myApp.PORT = '5556'

## PROTOCOL
## If customer is using TCPIP (PROTOCOL = 'TCPIP')
## Else leave blank (PROTOCOL = '')
myApp.PROTOCOL = 'TCPIP'

## GPRS USER NAME
## If GSM Provider requires GPRS User Name (USERNAME = 'JOE')
## Else leave blank (USERNAME = '')
myApp.USERNAME = ''

## GPRS PASSWORD
## If GSM Provider requires GPRS Password (PASSWORD = 'JOE123')
## Else leave blank (PASSWORD = '')
myApp.PASSWORD = ''

##--------------------------------------------------------------------------------------------------------------------
## End of Application Specific Configuration
##--------------------------------------------------------------------------------------------------------------------


##--------------------------------------------------------------------------------------------------------------------
## Main Function
##--------------------------------------------------------------------------------------------------------------------

try:

    main()
    print "Main Script Exit"

    #Inform Application that a Data Connection is not available
    JANUS_SER.set_DCD(0)
    
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot()

except:

    print "Main Script encountered an exception"
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> TerminusS2E"
     
    #Inform Application that a Data Connection is not available
    JANUS_SER.set_DCD(0)
    
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot() 