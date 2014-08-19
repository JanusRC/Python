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

import MDM      #code owned by: Telit
import MOD      #code owned by: Telit
import timers   #code owned by: Telit
import sys      #code owned by: Telit
import GPS      #code owned by: Telit


import ATC          #code owned by: Janus Remote Communications
import JANUS_SER    #code owned by: Janus Remote Communications
import JANUS_CONFIG #code owned by: Janus Remote Communications

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Clayton W. Knight, )   :   Initial release
##------------------------------------------------------------------------------------------------------------------

class SMSInfo:
    OriginatingPN = ''
    index = ''
    stat = ''
    alpha = ''
    date = ''
    time = ''
    SMS = ''


################################################################################################
## Methods for SMS sending/receiving and information parsing
################################################################################################

def configSMS():

    try:
        #Enable TEXT format for SMS Message
        res = ATC.sendAtCmd('AT+CMGF=1' ,ATC.properties.CMD_TERMINATOR,3,2)
        #no indications, we will poll manually
        res = ATC.sendAtCmd('AT+CNMI=0,0,0,0,0' ,ATC.properties.CMD_TERMINATOR,3,2)
        #Storage location
        res = ATC.sendAtCmd('AT+CPMS="SM"' ,ATC.properties.CMD_TERMINATOR,3,2)
        #Received SMS extra information display
        res = ATC.sendAtCmd('AT+CSDH=0' ,ATC.properties.CMD_TERMINATOR,3,2)

    except:
        printException("configSMS()")

    return

def CheckNewSMS():
# This function checks for a new SMS. If one is found it parses the information.

    # Input Parameter Definitions
    #   None
    #   Returns:
    #    String: Returns the received SMS
    #    0: Pass, no SMS received
    #   -1: Exception
    
    tmpReturn = '-1'

    try:
        #Now try to list all newly received SMS.
        #Using this method because the sendatcommand method ends up parsing out info we need due to the multiple \r\n response.
        res = MDM.send('AT+CMGL="REC UNREAD"', 0)
        res = MDM.sendbyte(0x0d, 0)
        #Grab the response of the command
        res = ATC.mdmResponse('OK', 10)
        
        #Try to list all currently stored SMS's. This is just a check to see if we have old/already read messages.
        res2 = MDM.send('AT+CMGL="ALL"', 0)
        res2 = MDM.sendbyte(0x0d, 0)
        #Grab the response of the command
        res2 = ATC.mdmResponse('OK', 10)      
        
        #Check for messages, search from 0 to the length of the AT Command response
        pos0 = res.find('+CMGL: 1',0,len(res))        
        GeneralCheck = res2.find('+CMGL:',0,len(res2))
        
        if (pos0 != -1):
            #New message found, let's parse the useful information
            #first, let's split the received information so we can echo a response to the originating phone number
            #Below is the normal response we are parsing
            #+CMGL: <index>,<stat>,<oa/da>,<alpha>,<scts><CR><LF><data><CR><LF>
            #+CMGL: 1,"REC UNREAD","+xxxxxxxxxxx","test","12/06/06,15:59:50-20"
            #Data

            #Separate by \r\n to separate the SMS data
            parts1 = res.split('\r\n')

             
            #Now split by comma to get individual data from the main chunk of information
            parts2 = parts1[1].split(",")

            SMSInfo.index = parts2[0]
            SMSInfo.stat = parts2[1]
            SMSInfo.OriginatingPN = parts2[2]
            SMSInfo.alpha = parts2[3]
            SMSInfo.date = parts2[4]
            SMSInfo.time = parts2[5]
            SMSInfo.SMS = parts1[2]

            #Delete ALL SMS to ensure a clear buffer for the next read
            res = ATC.sendAtCmd('AT+CMGD=1,4' ,ATC.properties.CMD_TERMINATOR,3,2)            

            return SMSInfo.SMS

        tmpReturn = '0'

        #Enter this AT command to ensure the buffer is empty and ready to receive new SMS messages
        if (GeneralCheck != -1):
            res = ATC.sendAtCmd('AT+CMGD=1,4' ,ATC.properties.CMD_TERMINATOR,3,2) 

    except:
        printException("CheckNewSMS")

    return tmpReturn

def SMSCommand(inStr):
# This function checks a newly received SMS for commands.
# If it finds specific command, using the header "CMD: " it will parse the command out, adjust the configuration parameter, and then respond to the originating PN as verification.
# If it finds an AT command, by simply finding AT it will take the command and carry it out, replying to the originating PN with the AT response.

    # Input Parameter Definitions
    #   inStr: The received SMS
    #   Returns:
    #    0: Pass, action carried out and SMS sent back
    #   -1: Exception
    #   -2: Pass, Unrecognized change command or AT command received though
    #   -3: Unrecognized SMS
    #   -4: Error sending an SMS to the originating P/N

    ##  Currently supported command list for things that can be altered. Simple list for now.
    ##  The user may also query the unit's information with a simple STATUS
    ##    INTERVAL
    ##    NOSWITCH
    ##    IGNITION
    ##    SLED
    ##    ULED
    ##    AUTOON

    tmpReturn = -1

    try:
        
        #Check for either change command or an AT command. Splitting ATCMD check into specifics because STATUS can trigger a generic AT check (alternative is to switch query word)
        changeCMD = inStr.find('CMD: ',0,len(inStr))
        ATCMD = inStr.find('AT',0,len(inStr))
        StatusQuery = inStr.find('STATUS',0,len(inStr))
        if (changeCMD != -1):
            #Change command found, take the commad, find what it's adjusting and then send an SMS back to the originator for verification
            #We know that it should be found at 0, and 5 characters after the command should start "CMD: x".
            ReceivedCmd = inStr[+5:len(inStr)]
                        
            if (ReceivedCmd == 'NOSWITCH = TRUE'):
                JANUS_CONFIG.Config.NOSWITCH = 'TRUE'
                JANUS_SER.sendUART("Switch Report : " + JANUS_CONFIG.Config.NOSWITCH + "\r\n")
                res = sendSMS("Switch Report : " + JANUS_CONFIG.Config.NOSWITCH,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'NOSWITCH = FALSE'):
                JANUS_CONFIG.Config.NOSWITCH = 'FALSE'
                JANUS_SER.sendUART("Switch Report : " + JANUS_CONFIG.Config.NOSWITCH + "\r\n")
                res = sendSMS("Switch Report : " + JANUS_CONFIG.Config.NOSWITCH,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'IGNITION = TRUE'):
                JANUS_CONFIG.Config.IGNITION = 'TRUE'
                JANUS_SER.sendUART("Ignition Report : " + JANUS_CONFIG.Config.IGNITION + "\r\n")
                res = sendSMS("Ignition Report : " + JANUS_CONFIG.Config.IGNITION,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'IGNITION = FALSE'):
                JANUS_CONFIG.Config.IGNITION = 'FALSE'
                JANUS_SER.sendUART("Ignition Report : " + JANUS_CONFIG.Config.IGNITION + "\r\n")
                res = sendSMS("Ignition Report : " + JANUS_CONFIG.Config.IGNITION,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'SLED = ON'):
                JANUS_CONFIG.Config.SLED = 'ON'
                JANUS_SER.sendUART("Cellular LED : " + JANUS_CONFIG.Config.SLED + "\r\n")
                res = sendSMS("Cellular LED : " + JANUS_CONFIG.Config.SLED,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'SLED = OFF'):
                JANUS_CONFIG.Config.SLED = 'OFF'
                JANUS_SER.sendUART("Cellular LED : " + JANUS_CONFIG.Config.SLED + "\r\n")
                res = sendSMS("Cellular LED : " + JANUS_CONFIG.Config.SLED,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'ULED = ON'):
                JANUS_CONFIG.Config.ULED = 'ON'
                JANUS_SER.sendUART("User LED : " + JANUS_CONFIG.Config.ULED + "\r\n")
                res = sendSMS("User LED : " + JANUS_CONFIG.Config.ULED,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'ULED = OFF'):
                JANUS_CONFIG.Config.ULED = 'OFF'
                JANUS_SER.sendUART("User LED : " + JANUS_CONFIG.Config.ULED + "\r\n")
                res = sendSMS("User LED : " + JANUS_CONFIG.Config.ULED,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'AUTOON = ON'):
                JANUS_CONFIG.Config.AUTOON = 'ON'
                JANUS_SER.sendUART("Auto ON : " + JANUS_CONFIG.Config.AUTOON + "\r\n")
                res = sendSMS("Auto ON : " + JANUS_CONFIG.Config.AUTOON,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'AUTOON = OFF'):
                JANUS_CONFIG.Config.AUTOON = 'OFF'
                JANUS_SER.sendUART("Auto ON : " + JANUS_CONFIG.Config.AUTOON + "\r\n")
                res = sendSMS("Auto ON : " + JANUS_CONFIG.Config.AUTOON,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd.find("INTERVAL") !=-1):
                #We have a GPS reporting interval change, make sure the value is between 1 and 86400
                #INTERVAL = xxx
                NewInterval = ReceivedCmd[+11:len(ReceivedCmd)]

                #Store original interval
                OrigInterval = JANUS_CONFIG.Config.INTERVAL

                #Change configuration interval
                JANUS_CONFIG.Config.INTERVAL = NewInterval

                if (int(JANUS_CONFIG.Config.INTERVAL) < 1 or int(JANUS_CONFIG.Config.INTERVAL) > 86400):
                    JANUS_SER.sendUART("Interval not in range (1 - 86400).\r\n")
                    res = sendSMS("Interval out of range (1 - 86400) : " + JANUS_CONFIG.Config.INTERVAL,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                    #Return the configuration to the original state
                    JANUS_CONFIG.Config.INTERVAL = OrigInterval
                    tmpReturn = -2
                else:
                    JANUS_SER.sendUART("Report Interval : " + JANUS_CONFIG.Config.INTERVAL + "\r\n")
                    res = sendSMS("Report Interval : " + JANUS_CONFIG.Config.INTERVAL,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                    tmpReturn = 0                    
            elif (ReceivedCmd == 'IGNITIONFOLLOW = TRUE'):
                JANUS_CONFIG.Config.IGNITIONFOLLOW = 'TRUE'
                JANUS_SER.sendUART("Ignition Follow : " + JANUS_CONFIG.Config.IGNITIONFOLLOW + "\r\n")
                res = sendSMS("Ignition Follow : " + JANUS_CONFIG.Config.IGNITIONFOLLOW,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            elif (ReceivedCmd == 'IGNITIONFOLLOW = FALSE'):
                JANUS_CONFIG.Config.IGNITIONFOLLOW = 'FALSE'
                JANUS_SER.sendUART("Ignition Follow : " + JANUS_CONFIG.Config.IGNITIONFOLLOW + "\r\n")
                res = sendSMS("Ignition Follow : " + JANUS_CONFIG.Config.IGNITIONFOLLOW,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = 0
            else:
                JANUS_SER.sendUART("Unrecognized/Unsupported Command Received: " + ReceivedCmd + "\r\n")
                res = sendSMS("Unrecognized/Unsupported Command Received: " + ReceivedCmd,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                tmpReturn = -2
                
            #Did we timeout or get an ERROR during the SMS sending?
            if (res.find("timeOut")!=-1 or res.find("ERROR") != -1):
                tmpReturn = -4

            #If we sucessfully changed the configuration amd sent the message, update and save the configuration file.
            if (tmpReturn == 0):
                res = JANUS_CONFIG.UpdateConfig()
                if (res == -1):
                    JANUS_SER.sendUART("Configuration Save Error.\r\n\r\n")
                    res = sendSMS("Configuration Save Error.",SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                    return
                else:
                    JANUS_SER.sendUART("Configuration file updated.\r\n\r\n")

        elif (StatusQuery != -1):
            #Status query for the module, pass back the current configuration values and location
            #This is the first elif to catch the STATUS check without accidentally triggering the general AT check
            JANUS_SER.sendUART("Status Query :\r\n")

            #The following are available through the included GPS module:
            #GPS.getActualPosition(), returns all fields like AT$GPSACP would
            #GPS.getLastGGA()
            #GPS.getLastGLL()
            #GPS.getLastGSA()
            #GPS.getLastGSV()
            #GPS.getLastRMC()
            #GPS.getLastVTG()
            #GPS.getPosition(), this gives LAT/LONG in numeric format

            #For the purposes of this demo, GLL will be used

            CurrentLocation = GPS.getLastRMC()
            QueryResponse = str("Unit: " + ATC.properties.IMEI+ "\r\n" +
                            "Switch Reporting: " + JANUS_CONFIG.Config.NOSWITCH + "\r\n" +
                            "Ignition Reporting: " + JANUS_CONFIG.Config.IGNITION + "\r\n" +
                            "Status LED: " + JANUS_CONFIG.Config.SLED + "\r\n" +
                            "User LED: " + JANUS_CONFIG.Config.ULED + "\r\n" +
                            "Auto ON: " + JANUS_CONFIG.Config.AUTOON + "\r\n" +
                            "Report Interval: " + JANUS_CONFIG.Config.INTERVAL + "\r\n" +
                            "Ignition Follow: " + JANUS_CONFIG.Config.IGNITIONFOLLOW + "\r\n" +
                            "Current Location: " + CurrentLocation + "\r\n")

            JANUS_SER.sendUART(QueryResponse)
            res = sendSMS(QueryResponse,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
            tmpReturn = 0

            #Did we timeout or get an ERROR during the SMS sending?
            if (res.find("timeOut")!=-1 or res.find("ERROR") != -1):
                tmpReturn = -4

        elif (ATCMD != -1):
            #AT command found, execute the command and pass back the response to the main program.
            #Using this instead of the sendatcommand method because it doesn't parse possibly useful information in an open ended response. 
            #res = MDM.send(inStr, 0)
            #res = MDM.sendbyte(0x0d, 0)
            #Grab the response of the command in it's entirety
            #ATCMDResponse = ATC.mdmResponse(ATC.properties.CMD_TERMINATOR, 10)

            ATCMDResponse = ATC.sendAtCmd(inStr ,ATC.properties.CMD_TERMINATOR,3,2)

            #Pass it to the UART and also send an SMS with the response.         
            JANUS_SER.sendUART(ATCMDResponse + "\r\n")
            res = sendSMS(ATCMDResponse,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
            tmpReturn = 0

            #Did we timeout or get an ERROR during the SMS sending?
            if (res.find("timeOut")!=-1 or res.find("ERROR") != -1):
                tmpReturn = -4

            #Did we get an ERROR from the AT command?
            if (ATCMDResponse.find("ERROR") != -1):
                tmpReturn = -2

        else:
            #Unrecognized SMS
            JANUS_SER.sendUART("Unrecognized/Unsupported SMS Received: " + inStr + "\r\n")
            tmpReturn = -3

            res = sendSMS("Unrecognized/Unsupported SMS Received: " + inStr,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
            tmpReturn = 0

            #Did we timeout or get an ERROR during the SMS sending? Otherwise just return the -3
            if (res.find("timeOut")!=-1 or res.find("ERROR") != -1):
                tmpReturn = -4            
            
    except:
        printException("SMSCommand()")

    return tmpReturn


def sendSMS(theSmsMsg,theDestination,theTerminator,retry,timeOut):
#This function sends an SMS Message

  # Input Parameter Definitions
  #   theSmsMsg: The text SMS Message
  #   theTerminator: string or character at the end of AT Command
  #   retry:  How many times the command will attempt to retry if not successfully send 
  #   timeOut: number of [1/10 seconds] command could take to respond

  #Note that the 145 being sent in with the destination address is the "type" of destination address, with 145 including a "+" for international
  while (retry != -1):
    print 'AT+CMGS="' + str(theDestination) + '",145'

    res = MDM.send('AT+CMGS="' + str(theDestination) + '",145', 0)
    res = MDM.sendbyte(0x0d, 0)
    res = ATC.mdmResponse('\r\n>', timeOut)
    print res 

    res = MDM.send(theSmsMsg, 0)
    res = MDM.sendbyte(0x1a, 0)

    #Wait for AT command response
    res = ATC.mdmResponse(theTerminator, timeOut)
      
    #Did AT command respond without error?
    pos1 = res.rfind(theTerminator,0,len(res))
    if (pos1 != -1):
      retry = -1
      res = ATC.parseResponse(res)
    else:
      retry = retry - 1
     
    print res

  #If the function fails to find the proper response to the SMS send ('OK<cr><lf>') then we receive a timeout string: 'timeOut'  
  return res

def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> JANUS_SMS"
    print "METHOD -> " + methodName

    return 