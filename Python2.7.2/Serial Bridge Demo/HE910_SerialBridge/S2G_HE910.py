#Demo HSPA910 Serial Bridge Program
# Janus Model#  HSPA910CF
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

import MDM                      #Telit AT Parser1
import SER                      #Telit SER interface (USIF0)
import MOD                      #Telit MOD library
import time                     #Telit Timer Library
import sys                      #Core Library

import conf
import ATC_HE910 as ATC         #ATC Library
import SER_HE910 as mySER       #Serial port library
import NET_HE910 as NETWORK     #Network Library
import SOCKET_HE910 as SOCKET   #Socket Connection Library
import IO_HE910 as myIO         #IO Control Library

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
##  5.)  The script can be exited by entering EXITSCR on USIF0 at any point, once it's seen the modem will reboot cleanly.
##------------------------------------------------------------------------------------------------------------------


def main():

    try:

        # Set Global Watchdog timeout in Seconds
        MOD.watchdogEnable(300)    

        #######################################
        ## Initialization
        #######################################
        
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


        mySER.sendUART("Beginning the serial bridge program. \r\n\r\n")        
        # Set Global Watchdog timeout in Seconds
        #MOD.watchdogEnable(300)


        #Get configuration from demo.conf file, transpose into new local myApp class
        myApp = conf.conf('/sys','demo.conf') 
        if myApp.CONF_STATUS != 0:
            mySER.sendUART("Demo configuration error: " + str(myApp.CONF_STATUS)) 
            return rtnList        

        
        mySER.sendUART("Configuration Loaded.\r\n")

        rtnList = myIO.init()
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning        
                
        mySER.sendUART("\r\nInitializing Network Setup. \r\n")
        #Set Network specific settings, wait for SIM card to be ready
        rtnList = NETWORK.initNetwork(myApp.ENS)
        if (rtnList[0] == -1) or (rtnList[0] == -2): raise UserWarning

        #Initialize SOCKET communications
        rtnList = SOCKET.init('1',myApp.APN)
        if (rtnList[0] == -1) or (rtnList[0] == -2): raise UserWarning

        mySER.sendUART("Network Setup Initialized. \r\n\r\n")
        
        #Update Unit information
        rtnList = ATC.getUnitInfo()
        if (rtnList[0] == -1): raise UserWarning     

        # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
        while (1):

            MOD.watchdogReset()

            #######################################
            ## Registration
            #######################################            

            RegCheck = 0 #Initialize check
            DataCheck = 0 #Initialize Check

            #What is the signal strength?
            rtnList = ATC.sendAtCmd('AT+CSQ',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2): raise UserWarning
            mySER.sendUART("Signal Strength (AT+CSQ): " + rtnList[1]  + "\r\n")
            

            #Wait until module is registered to GSM Network            
            mySER.sendUART("Checking Modem Registration. \r\n")
            rtnList = NETWORK.isRegistered(180)  #Wait 180 seconds for module to obtain GSM registration
            if (rtnList[0] == -1) or (rtnList[0] == -2): raise UserWarning

            if (rtnList[0] == 0): #Registered successfully
                RegCheck = 1
                mySER.sendUART("Modem Registered. \r\n\r\n")            

            #Wait until module is ready for data          
            mySER.sendUART("Checking Data Availability. \r\n")
            rtnList = NETWORK.isDataAttached(myApp.CGMM, 180)   #Wait 180 seconds for module to obtain GSM registration
            if (rtnList[0] == -1) or (rtnList[0] == -2): raise UserWarning

            if (rtnList[0] == 0): #Registered successfully
                DataCheck = 1
                mySER.sendUART("Modem ready for data. \r\n\r\n")

            #check for exit prompt, let's use command EXITSCR
            rtnList = mySER.readUART()
            if (rtnList[1].find('EXITSCR') != -1):
                print '\r\nExit Command Found\r\n'
                return                

            #######################################
            ## Socket Connection
            #######################################
                         
            # Loop while we're registered/ready
            while (RegCheck == 1 and DataCheck == 1):

                #check for exit prompt, let's use command EXITSCR
                rtnList = mySER.readUART()
                if (rtnList[1].find('EXITSCR') != -1):
                    print '\r\nExit Command Found\r\n'
                    return            

                rtnList = NETWORK.isRegistered(10)  #Fast reg check
                if (rtnList[0] == -1) or (rtnList[0] == -2): #unavailable, drill down discretely and show the status
                    RegCheck = 0
                    rtnList = ATC.sendAtCmd('AT+CREG?',ATC.properties.CMD_TERMINATOR,5)
                    mySER.sendUART("Registration Unavailable, Status: " + rtnList[1]  + "\r\n")
                    break #exit loop
                rtnList = NETWORK.isDataAttached(myApp.CGMM, 10) #Fast data check
                if (rtnList[0] == -1) or (rtnList[0] == -2): #unavailable, drill down discretely and show the status
                    DataCheck = 0
                    rtnList = ATC.sendAtCmd('AT+CGREG?',ATC.properties.CMD_TERMINATOR,5)
                    mySER.sendUART("Data Unavailable, Status: " + rtnList[1]  + "\r\n")
                    break #exit loop                


                #Open socket in online mode
                mySER.sendUART("Opening socket to server: " + myApp.IP + ":" + myApp.PORT + "\r\n")
                rtnList = SOCKET.openSocket(myApp.IP,myApp.PORT,1,myApp.USERNAME,myApp.PASSWORD,myApp.PROTOCOL,0)
                if (rtnList[0] == -1) or (rtnList[0] == -2): raise UserWarning

                #Check for open connection, this catches both online and command mode operations             
                if (rtnList[1] == "OK" or rtnList[1] == "CONNECT"): 
                     mySER.sendUART("Socket opened successfully.\r\n")   
                else:
                    mySER.sendUART("Connection failed to open, trying again. \r\n")
                                

                #Check for open socket
                DCD = MDM.getDCD()
                if (DCD == 1):
                    #Set DCD on USIF0
                    SER.setDCD(1)
                    #Forward CONNECT Message to Serial Port
                    mySER.sendUART('\r\nConnected to Server\r\n')
                    myIO.USER_LED('ON')

                    #######################################
                    ## Data exchange loop
                    #######################################

                    ##Loop while Socket connected. This loop operates on the notion that we are in online mode, so we are not using send_CM
                    while(1):

                        #Pet the watchdog
                        MOD.watchdogReset()

                        #Check for DCD active on MDM                        
                        DCD = MDM.getDCD()
                        if (DCD == 1):
                            #Outbound
                            #Get data from serial port, use function return
                            rtnList = mySER.readUART()
                            if (len(rtnList[1])!=0):
                                #Forward data to open socket if it's not empty and not the exit script command
                                
                                #check for exit prompt, let's use command EXITSCR
                                if (rtnList[1].find('EXITSCR') != -1): #exit found
                                    print '\r\nExit Command Found\r\n'
                                    print 'Exiting data mode\r\n'
                                    rtnList = SOCKET.exitDataMode()
                                    print 'Closing the socket\r\n'
                                    rtnList = SOCKET.closeSocket(1)
                                    return
                            
                                print rtnList[1] #Debug
                                res = MDM.send(rtnList[1],1)
                                
                            #Inbound
                            #Get data from open socket connection, straight MDM read
                            res = MDM.read()
                            if (len(res)!=0):
                                #Forward socket data to serial port
                                print res #Debug
                                mySER.sendUART(res)    

                        #When socket is closed exit loop via this path
                        #Will guarantee that '\r\nNO CARRIER\r\n' is sent every time
                        if (DCD == 0):
                            #Clear DCD on USIF0
                            SER.setDCD(0)
                            myIO.USER_LED('OFF')
                            #Get any remaining data from closed socket connection, straight MDM read
                            res = MDM.read()
                            if (len(res)!=0):
                                #Forward socket data to serial port
                                mySER.sendUART(res)   
                            break #exit loop to registration checks
                
                
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