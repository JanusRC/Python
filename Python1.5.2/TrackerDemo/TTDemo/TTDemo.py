#Demo Tracker Program for the Terminus Tracker
# Janus Model# N/A 
#
#Copyright © 2012, Janus Remote Communications
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
import GPS              #code owned by: Telit
import GPIO             #code owned by: Telit

import ATC              #code owned by: Janus Remote Communications
import JANUS_SER        #code owned by: Janus Remote Communications
import NETWORK          #code owned by: Janus Remote Communications
import GPRS             #code owned by: Janus Remote Communications
import JANUS_GPS        #code owned by: Janus Remote Communications
import JANUS_IO         #code owned by: Janus Remote Communications
import JANUS_SMS        #code owned by: Janus Remote Communications
import JANUS_CONFIG     #code owned by: Janus Remote Communications

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
        # Set Global Watchdog timeout in Seconds
        MOD.watchdogEnable(300)

        #Initialize the serial interface @ 115200, we must do this or nothing comes out the serial port
        res = JANUS_SER.init("115200",'8N1')
        if (res == -1):
            return

        JANUS_SER.sendUART("Beginning the Terminus Tracker Demo Program. \r\n\r\n")
        
        #Initialize the configuration, returns 0 for defaults, 1 for normal.
        ConfigLoad = JANUS_CONFIG.init()

        #Transpose the configuration list to myApp for usage here
        #We transpose only the main Config class to handle updates
        if (ConfigLoad == 0):
            myApp = JANUS_CONFIG.Config
            JANUS_SER.sendUART("Defaults Loaded.\r\n")
        elif (ConfigLoad == 1):
            myApp = JANUS_CONFIG.Config
            JANUS_SER.sendUART("Configuration File Loaded.\r\n")
        else:
            myApp = JANUS_CONFIG.Config
            JANUS_SER.sendUART("Configuration ERROR. Defaults Loaded.\r\n")

        #Initialize the I/O, turn on the stat LED
        res = JANUS_IO.init(myApp.SLED)
        if (res == -1):
            return

        #Read if Auto-On is active or not, 1 is active, 0 is inactive.  
        res = JANUS_IO.AutoONControl('READ', myApp.AUTOON)

        JANUS_SER.sendUART("\r\nAuto On: " + myApp.AUTOON + "\r\n")        

        #If Auto-on is OFF and we want it ON, set it.  
        if (res == 0 and myApp.AUTOON == 'ON'):
            res = JANUS_IO.AutoONControl('SET', myApp.AUTOON)            
            if (res == -1):
                return #Errored out
            elif (res == -2):
                JANUS_SER.sendUART("Timed out while waiting for MCU response. \r\n")
            elif (res == 1):
                JANUS_SER.sendUART("Auto ON Enabled. \r\n")

        #If Auto-on is ON and we want it OFF, set it.
        if (res == 1 and myApp.AUTOON == 'OFF'):
            res = JANUS_IO.AutoONControl('SET', myApp.AUTOON)
            if (res == -1):
                return #Errored out
            elif (res == -2):
                JANUS_SER.sendUART("Timed out while waiting for MCU response. \r\n")
            elif (res == 0):
                JANUS_SER.sendUART("Auto ON Disabled. \r\n")

        #If Auto-on is OFF, and we have it set as OFF. Let's see what caused this wake up and report it.
        #Although we can read IGN/SW directly, we check the MCU instead because they
        #May not be active as this point even though the MCU caught it.
    
        WakeupCause = ''
        if (res == 0 and myApp.AUTOON == 'OFF'):
            res = JANUS_IO.SW_IGN_Status()
            if (res == -1):
                return #Errored out
            elif (res == 0):
                JANUS_SER.sendUART("Wake up cause: N/O Switch \r\n")
                WakeupCause = 'Switch'
            elif (res == 1):
                JANUS_SER.sendUART("Wake up cause: Ignition \r\n")
                WakeupCause = 'Ignition'
            elif (res == 2):
                JANUS_SER.sendUART("Wake up cause: Both the Ignition and N/O Switch \r\n")
                WakeupCause = 'Both'
            elif (res == -2):
                JANUS_SER.sendUART("Wake up cause: Unknown \r\n")
                WakeupCause = 'Unknown'

                
        JANUS_SER.sendUART("\r\nInitializing Module GPRS. \r\n")
        #Set Network specific settings, wait for SIM card to be ready
        res = NETWORK.initGsmNetwork(myApp.NETWORK,myApp.BAND)
        if (res == -1):
            return

        #Init GPRS
        GPRS.init('1',myApp.APN)

        JANUS_SER.sendUART("GPRS Initialized. \r\n")
        
        ################################################################
        #### BEGIN Newly Added Config Stuff
        ################################################################

        #Initalize GPS
        JANUS_SER.sendUART("\r\nInitializing Module GPS. \r\n")
        res = JANUS_GPS.init(myApp.LNA)
        
        if (res != 0):
            JANUS_SER.sendUART("Failed to Initialize GPS, ERROR: " + res + "\r\n\r\n")
            return

        JANUS_SER.sendUART("GPS Initialized. \r\n\r\n")

        #Setup SMS
        if (myApp.SMS_ENABLED == 'TRUE'):
            JANUS_SER.sendUART("SMS Enabled, Initializing. \r\n")
            JANUS_SMS.configSMS()
            JANUS_SER.sendUART("SMS Initialized. \r\n\r\n")
        ################################################################
        #### END Newly Added Config Stuff
        ################################################################        

        # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
        while (1):
            
            MOD.watchdogReset()

            JANUS_SER.sendUART("Registering Module. \r\n")
            #Wait until module is registered to GSM Network
            res = NETWORK.isGsmRegistered(180)  #Wait 180 seconds for module to obtain GSM registration
            if (res == -1):
                return
            
            #Wait until module is attached to GPRS    
            res = NETWORK.isGprsAttached(180)  #Wait 180 seconds for module to obtain GPRS Attachment
            if (res == -1):
                return

            JANUS_SER.sendUART("Module Registered Successfully. \r\n\r\n")
            #############################################################################################################################
            ## Opening Socket Connection to Server
            ## We are opening in Command Mode to have the best control
            #############################################################################################################################

            #Update Unit information
            res = ATC.getUnitInfo()

            # Start timeout timer            
            timerB = timers.timer(0)
            timerB.start(int(myApp.INTERVAL))

            SwitchPos = 'Open' #Default State for Switch
            IgnPos = 'Inactive' #Default State for Switch

            FirstTimeThrough = 'TRUE' #Initialize flag for the first time running the connection/loop
            SENDSTRING = [] #Initialize the string list being sent to the server
            StringCount = 0
            # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
            while (1):
       
                while (1):

                    MOD.watchdogReset()

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
                    GPSPositionTemp = ''
                    GPSPositionTemp = GPS.getLastRMC()
                    GPSPositionTemp = GPSPositionTemp.rstrip()

                    #Update switch and ignition information
                    #We simply clear after the report is sent, so by default it's sent as Open/Inactive until it's read as the opposite.
                    #We're polling the MCU signals and then signaling back "we got the information" so we only read once, giving us one or both events to report
                        #    0: Pass, Switch is triggered
                        #    1: Pass, Ignition is triggered
                        #    2: Pass, BOTH are triggered
                        #   -1: Exception
                        #   -2: Pass, Neither is triggered

                    EventCheck = JANUS_IO.SW_IGN_Status()
                    if (EventCheck == 0): #Switch has been triggered
                        SwitchPos = 'Closed'
                        #JANUS_SER.sendUART("SwitchPos : " + SwitchPos + "\r\n")  

                    elif (EventCheck == 1): #Ignition has been triggered
                        IgnPos = 'Active'
                        #JANUS_SER.sendUART("IgnPos : " + IgnPos + "\r\n")

                    elif (EventCheck == 2): #Both have been triggered
                        SwitchPos = 'Closed'
                        IgnPos = 'Active'
                        #JANUS_SER.sendUART("IgnPos : " + IgnPos + "\r\n")
                        #JANUS_SER.sendUART("SwitchPos : " + SwitchPos + "\r\n")
                        
                    if (myApp.SMS_ENABLED == 'TRUE'):
                        res = JANUS_SMS.CheckNewSMS()
                        #If a new SMS is found and is valid, pass it to the command logic
                        if (res != '0'):
                            #We have received a new SMS, let's find what it wants us to do.
                            #JANUS_SER.sendUART("SMS Data : " + str(res) + "\r\n")
                            res = JANUS_SMS.SMSCommand(str(res))
                            #    0: Pass, action carried out and SMS sent back
                            #   -1: Exception
                            #   -2: Pass, Unrecognized change command or AT command received though
                            #   -3: Unrecognized SMS
                            #   -4: Error sending an SMS to the originating P/N
                            
                            if (res == -1):
                                return

                            #If the STAT LED was updated via SMS, let's adjust it                            
                            res = JANUS_IO.Cellular_LED(myApp.SLED)

                            #AUTO ON Run time Change.
                            #Read current Auto-On status, 1 is active, 0 is inactive.  
                            res = JANUS_IO.AutoONControl('READ', myApp.AUTOON)    

                            #The below will be ignored if there is no change
                            #If Auto-on is OFF and we want it ON, set it.  
                            if (res == 0 and myApp.AUTOON == 'ON'):
                                res = JANUS_IO.AutoONControl('SET', myApp.AUTOON)            
                                if (res == -1):
                                    return #Errored out
                                elif (res == -2):
                                    JANUS_SER.sendUART("Timed out while waiting for MCU response. \r\n")
                                elif (res == 1):
                                    JANUS_SER.sendUART("Auto ON Enabled. \r\n")

                            #If Auto-on is ON and we want it OFF, set it.
                            if (res == 1 and myApp.AUTOON == 'OFF'):
                                res = JANUS_IO.AutoONControl('SET', myApp.AUTOON)
                                if (res == -1):
                                    return #Errored out
                                elif (res == -2):
                                    JANUS_SER.sendUART("Timed out while waiting for MCU response. \r\n")
                                elif (res == 0):
                                    JANUS_SER.sendUART("Auto ON Disabled. \r\n")                          

                        elif (res == '-1'):
                            #Exception
                            return

                    #If interval timer expires then send packet to server
                    if (timerB.isexpired() or FirstTimeThrough == 'TRUE'):
                        
                        #The first time we drop into this loop we want to send data immediately, after that it's timer based sends.
                        FirstTimeThrough = 'FALSE' #Disable the flag
                        
                    #######################
                    ##BEGIN BUILDING STRING
                        #If we were woken up by one of the inputs, add it to the string to be sent
                        #This section can be used/altered to perhaps only display the wake up event for a certain amount of sends.
                        if (WakeupCause != ''):
                            WakeupString = WakeupCause
                            #JANUS_SER.sendUART("Wake up Event : " + WakeupCause + "\r\n")
                            #res = GPRS.send_CM("Wake up Event : " + WakeupCause + "\r\n",1,10)
                            #WakeupCause = '' #Clear the cause so it only gets reported the first time
                        else:
                            WakeupString = ''

                        #Build String to send to customer server, adjusts depending on what we want reported. Can only be one of these.
                        #CW Google Earth format
                        #STA = NMEA + ',' + IMEI + ',' + String1 + ',' + String2 + ',' + String3
                        #Strings 1/2/3 should remain in all sentences sent, but become null ('') when not being sent.
                        #The Strings follow a standard display format for the demo, so only send the actual information based on this format:
                        #String 1 will display in the Demo as "Switch"
                        #String 2 will display in the Demo as "Ignition"
                        #String 3 will display in the Demo as "Wake up Event"
                        if (myApp.NOSWITCH == 'TRUE' and myApp.IGNITION == 'TRUE'):
                            STA = GPSPositionTemp + ',' + ATC.properties.IMEI + ',' + SwitchPos + ',' + IgnPos + ',' + WakeupString
                        elif (myApp.NOSWITCH == 'TRUE' and myApp.IGNITION == 'FALSE'):
                            STA = GPSPositionTemp + ',' + ATC.properties.IMEI + ',' + SwitchPos + ',' + "" + ',' + WakeupString
                        elif (myApp.NOSWITCH == 'FALSE' and myApp.IGNITION == 'TRUE'):
                            STA = GPSPositionTemp + ',' + ATC.properties.IMEI + ',' + "" + ',' + IgnPos + ',' + WakeupString
                        elif (myApp.NOSWITCH == 'FALSE' and myApp.IGNITION == 'FALSE'):
                           STA = GPSPositionTemp + ',' + ATC.properties.IMEI + ',' + "" + ',' + "" + ',' + WakeupString

                        #Concatenate string, this allows store and forward during disconnects.
                        #STA is refreshed every time through, SENDSTRING is only cleared after a successful send
                        #Let's say 100B per string
                        #Max string length is 16kB, giving us (safely) 100 data points to store.
                        #This can be improved upon by utilizing a list, since each element in a list is capable of 16kB
                        #with a possible 4000 elements (keeping in mind overall memory limits)
                        if (StringCount < 100):
                            SENDSTRING.append(STA)
                            StringCount = StringCount+1
                        else:
                            JANUS_SER.sendUART("Store and forward limit reached (100). \r\n\r\n")
                    #######################
                    ##END BUILDING STRING

                        ###############################################################
                        ##### Socket Open Check
                        #If socket closed, open it
                        DCD = MDM.getDCD()
                        #Check for a valid SS too
                        res = ATC.sendAtCmd('AT#SS',ATC.properties.CMD_TERMINATOR,0,20)

                        #If there is not a valid DCD OR the socket status shows that there is no socket open.
                        #We check for both because DCD seems to get stuck on 1 under certain conditions and we cannot set it, yet SS works fine.
                        if (DCD == 0 or res == "#SS: 1,0"): 
                            JANUS_SER.sendUART("Opening socket to server: " + myApp.IP + ":" + myApp.PORT + "\r\n")
                            #Connect to customer's server
                            res = GPRS.openSocket(myApp.IP,myApp.PORT,1,myApp.USERNAME,myApp.PASSWORD,myApp.PROTOCOL,1)
                            if (res != 0):
                                JANUS_SER.sendUART("Connection failed to open. \r\n")
                                #Turn OFF the LED permanently until we have a valid connection
                                res = JANUS_IO.GPS_LED('OFF', myApp.ULED)
                            elif (res == 0):
                                JANUS_SER.sendUART("Socket opened successfully.\r\n")
                                #Turn ON the LED to show we have a valid connection
                                res = JANUS_IO.GPS_LED('ON', myApp.ULED)
                                JANUS_SER.sendUART("Polling GPS receiver for current location every " +  myApp.INTERVAL + " second(s)\r\n")                             

                            #Do not return, end of this loop will handle the service checking
                        ###############################################################
                        ##### Socket Open Check
                        try:
                            #If socket open upload data
                            DCD = MDM.getDCD()
                            #Check for a valid SS too
                            res = ATC.sendAtCmd('AT#SS',ATC.properties.CMD_TERMINATOR,0,20)

                            #If there is a valid DCD AND the socket status shows that there is a valid socket connection too.
                            #We check for both because DCD seems to get stuck on 1 under certain conditions and we cannot set it, yet SS works fine.
                            if (DCD == 1 and res != "#SS: 1,0"):

                                #Update the GPS LED. This will turn the LED on/off during run time if it has been updated via SMS.
                                #Defaulted to ON
                                res = JANUS_IO.GPS_LED('ON', myApp.ULED)

                                #####Placeholder for built string OLD spot

                                #Strip the last entry of the pipe
                                #Pop the last item out, remove the last byte (the pipe) then append it back to the list.
                                #This covers single sends and block sends
##                                LastItem = SENDSTRING.pop(StringCount-1)
##                                ItemLength = len(LastItem)
##                                LastItem = LastItem[0:ItemLength-1]
##                                SENDSTRING.append(LastItem)

                                JANUS_SER.sendUART("Sending data: \r\n")

                                res = 0
                                x = 0
                                while (res == 0 and x < StringCount):
                                    #Send Data
                                    JANUS_SER.sendUART(str(SENDSTRING[x]) + "\r\n")
                                    res = GPRS.send_CM(SENDSTRING[x],1,10)
                                    x = x+1

                                if (res == 1):
                                    JANUS_SER.sendUART("\r\n\r\nData Empty, Error receiving info from GPS module\r\n")
                                    return
                                if (res == -2):
                                    JANUS_SER.sendUART("\r\n\r\nTimed out while sending data, checking socket connection\r\n") #Do not return, drop to service checks
                                    #Add the pipe to the end again since this got disconnected mid-send procedure and will become a store and forward send.
##                                    LastItem = SENDSTRING.pop(StringCount-1)
##                                    LastItem = LastItem + '|'
##                                    SENDSTRING.append(LastItem)
                                else:
                                    JANUS_SER.sendUART("\r\n\r\nData Sent Successfully.\r\n\r\n")
                                    #Blink OFF the LED to indicate data was sent
                                    res = JANUS_IO.GPS_LED('OFF', myApp.ULED)
                                    res = JANUS_IO.GPS_LED('ON', myApp.ULED)


                                    if (IgnPos == 'Inactive' and myApp.AUTOON == 'OFF' and myApp.IGNITIONFOLLOW == 'TRUE'):
                                        #Special Case, auto-on is not active and we want to only be active while the ignition is active.
                                        #Inigition has dropped, we've sent the last data packet, now shut the unit down
                                        res = ATC.sendAtCmd('AT#SHDN',ATC.properties.CMD_TERMINATOR,0,20)

                                    #Put the Switch and Ignition I/O back to default, clear the list and counter
                                    SwitchPos = 'Open'
                                    IgnPos = 'Inactive'
                                    SENDSTRING = []
                                    StringCount = 0
                                
                                #Exit data mode
                                #DEBUG.sendMsg('Exiting data mode\r\n') 
                                #res = ATC.exitSocketDataMode()

                                #Close Socket
                                #Pass in: sockNum
                                #res = ATC.closeSocket('1')
                                #DEBUG.sendMsg('Connection closed\r\n') 

                                break

                            else:
                                JANUS_SER.sendUART("\r\nConnection not available, checking status.\r\n")

                                #Wait until module is registered to GSM Network
                                #res = NETWORK.isGsmRegistered(180)  #Wait 180 seconds for module to obtain GSM registration
                                #if (res == -1):
                                #    ATC.reboot()

                                #Wait until module is attached to GPRS    
                                #res = NETWORK.isGprsAttached(180)  #Wait 180 seconds for module to obtain GPRS Attachment
                                #if (res == -1):
                                #    ATC.reboot()

                                #What is the signal strength?
                                res = ATC.sendAtCmd('AT+CSQ',ATC.properties.CMD_TERMINATOR,0,5)
                                JANUS_SER.sendUART("Signal Strength (AT+CSQ): " + res + "\r\n")

                                #Still registered?
                                res = ATC.sendAtCmd('AT+CREG?',ATC.properties.CMD_TERMINATOR,0,5)
                                JANUS_SER.sendUART("Registration Check (AT+CREG?): " + res + "\r\n")

                                #GPRS Available?
                                res = ATC.sendAtCmd('AT+CGREG?',ATC.properties.CMD_TERMINATOR,0,5)
                                JANUS_SER.sendUART("GPRS  Availability (AT+CGREG?): " + res + "\r\n")                                

                                #Is a PDP context activated?
                                res = ATC.sendAtCmd('AT#SGACT?',ATC.properties.CMD_TERMINATOR,0,20)
                                JANUS_SER.sendUART("PDP Context status (AT#SGACT?): " + res + "\r\n\r\n")

                                break                             

                        except:
                            JANUS_SER.sendUART("Script encountered an exception while uploading data to server\r\n")
                            JANUS_SER.sendUART("Exception Type: " + str(sys.exc_type) + "\r\n")
                            JANUS_SER.sendUART("MODULE -> LobosTrack\r\n")
                            break

                ## Re-Start timeout timer
                timerB = timers.timer(0)
                timerB.start(int(myApp.INTERVAL))

                #DEBUG.CLS()   #Clear screen command for VT100 terminals

    except:
        print "Script encountered an exception"
        print "Exception Type: " + str(sys.exc_type)
        print "MODULE -> TerminusS2E"
        
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
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> LobosTrack"
    
    #Reboot or Script will not restart until a power cycle occurs
    ATC.reboot() 