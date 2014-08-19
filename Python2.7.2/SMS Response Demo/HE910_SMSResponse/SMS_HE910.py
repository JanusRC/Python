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

import MDM

import time
import sys
import GPS


import ATC_HE910 as ATC
import SER_HE910 as mySER
import IO_HE910

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

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data


        #Enable TEXT format for SMS Message
        a = ATC.sendAtCmd('AT+CMGF=1',ATC.properties.CMD_TERMINATOR,5)
        #no indications, we will poll manually
        b = ATC.sendAtCmd('AT+CNMI=0,0,0,0,0',ATC.properties.CMD_TERMINATOR,5)
        #Storage location
        c = ATC.sendAtCmd('AT+CPMS="SM"',ATC.properties.CMD_TERMINATOR,5)
        #Received SMS extra information display
        d = ATC.sendAtCmd('AT+CSDH=0',ATC.properties.CMD_TERMINATOR,5)

        if (    a == -1
            or b == -1
            or c == -1
            or d == -1
            ):
            return rtnList    #Errored out
            

        rtnList[0] = 0  #no error, no data  

    except:
        print sys.exc_info()
        rtnList[0] = -1


    return rtnList

def CheckNewSMS():
# This function checks for a new SMS. If one is found it parses the information.
  
    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no SMS
        #    1:    No errors occurred, return received SMS

        #Now try to list all newly received SMS.
        #Using this method because the sendatcommand method ends up parsing out info we need due to the multiple \r\n response.
        rtnList[1] = MDM.send('AT+CMGL="REC UNREAD"', 0)
        rtnList[1] = MDM.sendbyte(0x0d, 0)
        #Grab the response of the command
        rtnList = ATC.mdmResponse('OK', 10)

        res  = rtnList[1]        
        
        #Try to list all currently stored SMS's. This is just a check to see if we have old/already read messages.
        rtnList[1] = MDM.send('AT+CMGL="ALL"', 0)
        rtnList[1] = MDM.sendbyte(0x0d, 0)
        #Grab the response of the command
        rtnList = ATC.mdmResponse('OK', 10)

        res2 = rtnList[1]        
        
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
            rtnList = ATC.sendAtCmd('AT+CMGD=1,4' ,ATC.properties.CMD_TERMINATOR,5)            

            rtnList[1] = SMSInfo.SMS
            rtnList[0] = 1 #indicate data received

            return rtnList            
        

        #Enter this AT command to ensure the buffer is empty and ready to receive new SMS messages
        if (GeneralCheck != -1):
            rtnList = ATC.sendAtCmd('AT+CMGD=1,4' ,ATC.properties.CMD_TERMINATOR,5)


        rtnList[0] = 0 #No errors, but no data received
        
    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def SMSCommand(inStr):
# This function checks a newly received SMS for commands.
# If it finds specific command, using the header "CMD: " it will parse the command out, adjust the configuration parameter, and then respond to the originating PN as verification.
# If it finds an AT command, by simply finding AT it will take the command and carry it out, replying to the originating PN with the AT response.

    # Input Parameter Definitions
    #   inStr: The received SMS

    ##  Currently supported command list for things that can be altered. Simple list for now.
    ##  The user may also query the unit's information with a simple STATUS
    ##    SLED
    ##    ULED


    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   Returns:
        #    0: Pass, action carried out and SMS sent back
        #   -1: Exception
        #   -2: Pass, Unrecognized change command or AT command received though
        #   -3: Unrecognized SMS
        #   -4: Error sending an SMS to the originating P/N     
        
        #Check for either change command or an AT command. Splitting ATCMD check into specifics because STATUS can trigger a generic AT check (alternative is to switch query word)
        changeCMD = inStr.find('CMD: ',0,len(inStr))
        ATCMD = inStr.find('AT',0,len(inStr))
        StatusQuery = inStr.find('STATUS',0,len(inStr))
        if (changeCMD != -1):
            #Change command found, take the commad, find what it's adjusting and then send an SMS back to the originator for verification
            #We know that it should be found at 0, and 5 characters after the command should start "CMD: x".
            ReceivedCmd = inStr[+5:len(inStr)]              
            
            if (ReceivedCmd == 'SLED = ON'):
                mySER.sendUART("Cellular LED : ON \r\n\r\n")
                rtnList = IO_HE910.Cellular_LED('ON')
                rtnList = sendSMS("Cellular LED : ON",SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                rtnList[0] = 0
            elif (ReceivedCmd == 'SLED = OFF'):
                mySER.sendUART("Cellular LED : OFF \r\n\r\n")
                rtnList = IO_HE910.Cellular_LED('OFF')
                rtnList = sendSMS("Cellular LED : OFF",SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                rtnList[0] = 0
            elif (ReceivedCmd == 'ULED = ON'):
                mySER.sendUART("User LED : ON \r\n\r\n")
                rtnList = IO_HE910.USER_LED('ON')
                rtnList = sendSMS("User LED : ON",SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                rtnList[0] = 0
            elif (ReceivedCmd == 'ULED = OFF'):
                mySER.sendUART("User LED : OFF \r\n\r\n")
                rtnList = IO_HE910.USER_LED('OFF')
                rtnList = sendSMS("User LED : OFF",SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                rtnList[0] = 0
            else:
                mySER.sendUART("Unrecognized/Unsupported Command Received: " + ReceivedCmd + "\r\n\r\n")
                rtnList = sendSMS("Unrecognized Command Received: " + ReceivedCmd,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
                rtnList[0] = -2
                
            #Did we timeout or get an ERROR during the SMS sending?
            if (rtnList[1].find("timeOut")!=-1 or rtnList[1].find("ERROR") != -1):
                rtnList[0] = -4


        elif (StatusQuery != -1):
            #Status query for the module, pass back the current configuration values and location
            #This is the first elif to catch the STATUS check without accidentally triggering the general AT check
            mySER.sendUART("Status Query :\r\n")

            #Check the CELL LED Status to report
            rtnList = ATC.sendAtCmd('AT#GPIO=1,2' ,ATC.properties.CMD_TERMINATOR,5)
            #GPIO: 2,0
            if (rtnList[1].find('#GPIO: 2') != -1):
                CELL_LED = 'ON'
            else:
                CELL_LED = 'OFF'

            #Check the GPS/USER LED Status to report
            rtnList = ATC.sendAtCmd('AT#GPIO=2,2' ,ATC.properties.CMD_TERMINATOR,5)
            #GPIO: 2,0
            if (rtnList[1].find('#GPIO: 1,1') != -1):
                USER_LED = 'ON'
            else:
                USER_LED = 'OFF'
            
            
            

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

            CurrentLocation = GPS.getLastRMC()
            QueryResponse = str("Unit: " + ATC.properties.IMEI+ "\r\n" +
                            "Status LED: " + CELL_LED + "\r\n" +
                            "USER LED: " + USER_LED + "\r\n" +
                            "Current Location: " + CurrentLocation + "\r\n")

            mySER.sendUART(QueryResponse)
            rtnList = sendSMS(QueryResponse,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
            rtnList[0] = 0

            #Did we timeout or get an ERROR during the SMS sending?
            if (rtnList[1].find("timeOut")!=-1 or rtnList[1].find("ERROR") != -1):
                rtnList[0] = -4

        elif (ATCMD != -1):
            #AT command found, execute the command and pass back the response to the main program.
            #Using this instead of the sendatcommand method because it doesn't parse possibly useful information in an open ended response. 
            #res = MDM.send(inStr, 0)
            #res = MDM.sendbyte(0x0d, 0)
            #Grab the response of the command in it's entirety
            #ATCMDResponse = ATC.mdmResponse(ATC.properties.CMD_TERMINATOR, 10)

            ATCMDResponse = ATC.sendAtCmd(inStr ,ATC.properties.CMD_TERMINATOR,5)

            #Did we get an ERROR from the AT command?
            if (ATCMDResponse[1].find("ERROR") != -1):
                rtnList[0] = -2            

            #Pass it to the UART and also send an SMS with the response.         
            mySER.sendUART(ATCMDResponse[1] + "\r\n\r\n")
            rtnList = sendSMS(ATCMDResponse[1],SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
            rtnList[0] = 0

            #Did we timeout or get an ERROR during the SMS sending?
            if (rtnList[1].find("timeOut")!=-1 or rtnList[1].find("ERROR") != -1):
                rtnList[0] = -4



        else:
            #Unrecognized SMS
            mySER.sendUART("Unrecognized/Unsupported Command Received: " + inStr + "\r\n\r\n")
            

            rtnList = sendSMS("Unrecognized/Unsupported SMS Received: " + inStr,SMSInfo.OriginatingPN,ATC.properties.CMD_TERMINATOR,3,180)
            rtnList[0] = -3

            #Did we timeout or get an ERROR during the SMS sending? Otherwise just return the -3
            if (rtnList[1].find("timeOut")!=-1 or rtnList[1].find("ERROR") != -1):
                rtnList[0] = -4            
            

    except:
        print sys.exc_info()
        rtnList[0] = -1


    return rtnList


def sendSMS(theSmsMsg,theDestination,theTerminator,retry,timeOut):
#This function sends an SMS Message

  # Input Parameter Definitions
  #   theSmsMsg: The text SMS Message
  #   theTerminator: string or character at the end of AT Command
  #   retry:  How many times the command will attempt to retry if not successfully send 
  #   timeOut: number of [1/10 seconds] command could take to respond

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data        

      #Note that the 145 being sent in with the destination address is the "type" of destination address, with 145 including a "+" for international
        while (retry != -1):

            rtnList[1] = MDM.send('AT+CMGS="' + str(theDestination) + '",145', 0)
            rtnList[1] = MDM.sendbyte(0x0d, 0)
            rtnList = ATC.mdmResponse('\r\n>', timeOut)

            rtnList[1] = MDM.send(theSmsMsg, 0)
            rtnList[1] = MDM.sendbyte(0x1a, 0)

            #Wait for AT command response
            rtnList = ATC.mdmResponse(theTerminator, timeOut)
              
            #Did AT command respond without error?
            pos1 = rtnList[1].rfind(theTerminator,0,len(rtnList[1]))
            if (pos1 != -1):
              retry = -1
              rtnList = ATC.parseResponse(rtnList[1])
            else:
              retry = retry - 1
     
        rtnList[0] = 0  #no error, no data  

  #If the function fails to find the proper response to the SMS send ('OK<cr><lf>') then we receive a timeout string: 'timeOut'  
    except:
        print sys.exc_info()
        rtnList[0] = -1


    return rtnList

