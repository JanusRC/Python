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

import GPS          #code owned by: Telit
import MDM          #code owned by: Telit
import MOD          #code owned by: Telit
import timers       #code owned by: Telit

import ATC          #code owned by: Janus Remote Communications
import JANUS_SER    #code owned by: Janus Remote Communications

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Clayton W. Knight, )   :   Initial release
##------------------------------------------------------------------------------------------------------------------

#Name of the configuration file to be created/used
theFile = 'settings.txt'  

class Config:
    #This is the configuration that will be filled from the configuration file
    BAND = ''
    NETWORK = ''
    APN = ''
    IP = ''
    PORT = ''
    PROTOCOL = ''
    USERNAME = ''
    PASSWORD = ''
    SMS_ENABLED = ''
    SMS = ''
    INTERVAL = ''
    LNA = ''
    NOSWITCH = ''
    IGNITION = ''
    SLED = ''
    ULED = ''
    AUTOON = ''
    IGNITIONFOLLOW = ''

class DefaultConfig:
    #This is the default configuration that will be loaded if there is no configuration file to read from
    BAND = ''
    NETWORK = ''
    APN = ''
    IP = ''
    PORT = ''
    PROTOCOL = ''
    USERNAME = ''
    PASSWORD = ''
    SMS_ENABLED = ''
    SMS = ''
    INTERVAL = ''
    LNA = ''
    NOSWITCH = ''
    IGNITION = ''
    SLED = ''
    ULED = ''
    AUTOON = ''
    IGNITIONFOLLOW = ''


def init():
    #Initializes the configuration for application use
    # Input Parameter Definitions
    #   None
    #
    #   Returns:
    #    0: Defaults being used
    #    1: Saved Configuration file values being used
    #   -1: Exception, main app will load defaults

    JANUS_SER.sendUART("Initializing The Configuration. \r\n")
    
    tmpReturn = -1
    #This will first check if there is a configuration file. If there is not one it will create one with the default configuration, transposing that default configuration
    #To the application's class for usage. If there is one it will read the configuration and load it into the application's class for usage.

    #Fill the default values from the user entered data. This data will be used if there are issues with the configuration file
    res = FillDefault()

    # Check if the configuration file exists (this is only really for the first runthrough)
    try:
        f = open(theFile,'r')
        NoFile = 'False'
    except:
        #No file found, flag it
        JANUS_SER.sendUART("Configuration file does not exist. \r\n")
        NoFile = 'True'
        
    #If successful the file is now open for reading, otherwise create a new default file

    try:
        if (NoFile == 'True'):
            #No file found, create one from the default configuration
            JANUS_SER.sendUART("Creating File With Default Values. \r\n")
            f = open(theFile,'w')

            #Create a string list to write to the file
            DefaultList = Class2List(DefaultConfig)
            f.write(DefaultList)
            f.close()
            
            JANUS_SER.sendUART("Settings file created.\r\n")

##            #Before we finish, let's read it back and populate the Config fields
##            #Otherwise if we were to save after loading defaults, we may accidentally write
##            #blank information to the file
##            f = open(theFile,'r')
##            filedump = f.read()
##            f.close()
##
##            list1 = filedump.split('\r\n')       
##            res = List2Config(list1)

            #Return 0 to indicate we are using default values
            if (res == 0):
                tmpReturn = 0
            
        else:
            #Read the file
            JANUS_SER.sendUART("File Found, loading values. \r\n")
            filedump = f.read()
            f.close()
            
            list1 = filedump.split('\r\n')       
            res = List2Config(list1)

            #Return 1 to indicate configuration file values are being loaded
            if (res == 0):
                tmpReturn = 1
        
    except:
        JANUS_SER.sendUART("Error with file manipulation. \r\n")

    return tmpReturn

def UpdateConfig():
    #Updates the current configuration file from the Config class. 
    # Input Parameter Definitions
    #   None
    #
    #   Returns:
    #    1: configuration file updated
    #   -1: Exception
    
    tmpReturn = -1

    try:

        JANUS_SER.sendUART("\r\nUpdating the configuration file: " + theFile + "\r\n")
        f = open(theFile,'w')
        #Create string list for writing
        List2 = Class2List(Config)
        
        f.write(List2)
        f.close()
        
        tmpReturn = 1

    except:
        printException("UpdateConfig")
        JANUS_SER.sendUART("UpdateConfig exception. \r\n")  

    return tmpReturn



def Class2List(inClass):
    #Takes the input class and converts it into a string list for writing
    # Input Parameter Definitions
    #   inClass: input class to convert to standard layout string for writing
    #
    #   Returns:
    #    String: Returns the created string
    #   -1: Exception
    
    ##  Standard Layout  
    ##    BAND = ''
    ##    NETWORK = ''
    ##    APN = ''
    ##    IP = ''
    ##    PORT = ''
    ##    PROTOCOL = ''
    ##    USERNAME = ''
    ##    PASSWORD = ''
    ##    SMS_ENABLED = ''
    ##    SMS = ''
    ##    INTERVAL = ''
    ##    LNA = ''
    ##    NOSWITCH = ''
    ##    IGNITION = ''
    ##    SLED = ''
    ##    ULED = ''
    ##    AUTOON = ''
    ##    IGNITIONFOLLOW = ''

    
    tmpReturn = -1
    try:
        #Create list in the form of the class, ending each with \r\n
        ConfigList = str("BAND = " + str(inClass.BAND) + "\r\n" +
                        "NETWORK = " + str(inClass.NETWORK) + "\r\n"
                        "APN = " + inClass.APN + "\r\n"
                        "IP = " + inClass.IP + "\r\n"
                        "PORT = " + inClass.PORT + "\r\n"
                        "PROTOCOL = " + inClass.PROTOCOL + "\r\n"
                        "USERNAME = " + inClass.USERNAME + "\r\n"
                        "PASSWORD = " + inClass.PASSWORD + "\r\n"
                        "SMS_ENABLED = " + inClass.SMS_ENABLED + "\r\n"
                        "SMS = " + inClass.SMS + "\r\n"
                        "INTERVAL = " + inClass.INTERVAL + "\r\n"
                        "LNA = " + inClass.LNA + "\r\n"
                        "NOSWITCH = " + inClass.NOSWITCH + "\r\n"
                        "IGNITION = " + inClass.IGNITION + "\r\n"
                        "SLED = " + inClass.SLED + "\r\n"
                        "ULED = " + inClass.ULED + "\r\n"
                        "AUTOON = " + inClass.AUTOON + "\r\n"
                        "IGNITIONFOLLOW = " + inClass.IGNITIONFOLLOW)
        
        tmpReturn = ConfigList

    except:
        printException("Class2List")
        JANUS_SER.sendUART("Class2List exception. \r\n")  


    return tmpReturn

def List2Config(inList):
    #Takes the input List and converts it into the Config class for application usage.
    #If an entry pulled from the configuration file is unrecognizable/incorrect/entered wrong it will bypass and use the default value.
    # Input Parameter Definitions
    #   inList: input list derived from the read configuration file
    #
    #   Returns:
    #    0: Pass
    #    1: Configuration file length not valid
    #   -1: Exception
    
    ##  Standard Layout  
    ##    BAND = ''
    ##    NETWORK = ''
    ##    APN = ''
    ##    IP = ''
    ##    PORT = ''
    ##    PROTOCOL = ''
    ##    USERNAME = ''
    ##    PASSWORD = ''
    ##    SMS_ENABLED = ''
    ##    SMS = ''
    ##    INTERVAL = ''
    ##    LNA = ''
    ##    NOSWITCH = ''
    ##    IGNITION = ''
    ##    SLED = ''
    ##    ULED = ''
    ##    AUTOON = ''
    ##    IGNITIONFOLLOW = ''

    
    tmpReturn = -1

    try:
        
        if (len(inList)> 0):
            JANUS_SER.sendUART(str(len(inList)) + " of 18 entries found \r\n")  
            for x in inList:
                #JANUS_SER.sendUART(str(x) + "\r\n")  
                #We know the "=" will be found at 0 and 2 characters after it will start until the
                #end of the line. It's split previously by \r\n so there is no \r\n to locate at the end
                posbegin = x.find('=',0,len(x))

                #We have our position, now let's find the entry type and data
                entryType = x[0:posbegin-1]
                entryData = x[posbegin+2:len(x)]

                if (entryType == "BAND"):
                    #Verify BAND is a number between 0 and 3
                    try:
                        if ((int(entryData) < 0) or (int(entryData) > 3)):
                            JANUS_SER.sendUART("BAND out of range: " + str(entryData) + "\r\n")
                            JANUS_SER.sendUART("Using Default Value: " + str(Config.BAND) + "\r\n")
                        else:
                            #Passes, use the value
                            Config.BAND = entryData
                    except:
                        JANUS_SER.sendUART("BAND not a valid integer: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.BAND) + "\r\n")
                elif (entryType == "NETWORK"):
                    if ((entryData != 'ATT') and (entryData != 'GSM')):
                        JANUS_SER.sendUART("NETWORK not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.NETWORK) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.NETWORK = entryData
                elif (entryType == "APN"):
                    #Not sure on how to test this yet, just use the value
                    Config.APN = entryData
                elif (entryType == "IP"):
                    tmp_list = entryData.split('.')
                    #Does IP address have 4 Octets?
                    if (len(tmp_list)==4):
                        errorflag = 0
                        for y in tmp_list:
                            #Verify each octet is a number between 0 and 255
                            try:
                                if ((int(y) < 0) or (int(y) > 255)):
                                    JANUS_SER.sendUART("Octet " + str(y) + " out of range: " + str(entryData) + "\r\n")
                                    JANUS_SER.sendUART("Using Default Value: " + str(Config.IP) + "\r\n")
                                    errorflag = 1
                            except:
                                JANUS_SER.sendUART("Octet " + str(y) + " not a valid integer: " + str(entryData) + "\r\n")
                                JANUS_SER.sendUART("Using Default Value: " + str(Config.IP) + "\r\n")
                                errorflag = 1
                        if (errorflag == 0):
                            #Passes without error, use the value
                            Config.IP = entryData
                    else:
                        JANUS_SER.sendUART("IP does not have enough octets " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.IP) + "\r\n")
                elif (entryType == "PORT"):
                    #Verify PORT is a number between 0 and 65535
                    try:
                        if ((int(entryData) < 0) or (int(entryData) > 65535)):
                            JANUS_SER.sendUART("PORT out of range: " + str(entryData) + "\r\n")
                            JANUS_SER.sendUART("Using Default Value: " + str(Config.PORT) + "\r\n")
                        else:
                            #Passes, use the value
                            Config.PORT = entryData
                    except:
                            JANUS_SER.sendUART("PORT not a valid integer: " + str(entryData) + "\r\n")
                            JANUS_SER.sendUART("Using Default Value: " + str(Config.PORT) + "\r\n")
                elif (entryType == "PROTOCOL"):
                    if ((entryData != 'UDP') and (entryData != 'TCPIP')):
                        JANUS_SER.sendUART("PROTOCOL not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.PROTOCOL) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.PROTOCOL = entryData
                elif (entryType == "USERNAME"):
                    Config.USERNAME = entryData
                elif (entryType == "PASSWORD"):
                    Config.PASSWORD = entryData
                elif (entryType == "SMS_ENABLED"):
                    if ((entryData != 'TRUE') and (entryData != 'FALSE')):
                        JANUS_SER.sendUART("SMS_ENABLED not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.SMS_ENABLED) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.SMS_ENABLED = entryData
                elif (entryType == "SMS"):
                    tmpEntry = entryData.find('+',0,len(entryData))
                    if (tmpEntry != -1):
                        #Check length, should be 12 +xxxxxxxxxxx
                        if (len(entryData) == 12):
                            Config.SMS = entryData
                        else:
                            JANUS_SER.sendUART("SMS number not a valid length: " + str(entryData) + "\r\n")
                            JANUS_SER.sendUART("Using Default Value: " + str(Config.SMS) + "\r\n")
                    else:
                        JANUS_SER.sendUART("SMS number not a valid format: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.SMS) + "\r\n")
                elif (entryType == "INTERVAL"):
                    #INTERVAL is a number in seconds between 1 and 86400 (One Day Maximum)
                    try:
                        if ((int(entryData) < 1) or (int(entryData) > 86400)):
                            JANUS_SER.sendUART("INTERVAL out of range: " + str(entryData) + "\r\n")
                            JANUS_SER.sendUART("Using Default Value: " + str(Config.INTERVAL) + "\r\n")
                        else:
                            #Passes, use the value
                            Config.INTERVAL = entryData
                    except:
                        JANUS_SER.sendUART("INTERVAL not a valid integer: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.INTERVAL) + "\r\n")
                elif (entryType == "LNA"):
                    if ((entryData != 'TRUE') and (entryData != 'FALSE')):
                        JANUS_SER.sendUART("LNA not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.LNA) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.LNA = entryData
                elif (entryType == "NOSWITCH"):
                    if ((entryData != 'TRUE') and (entryData != 'FALSE')):
                        JANUS_SER.sendUART("NOSWITCH not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.NOSWITCH) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.NOSWITCH = entryData
                elif (entryType == "IGNITION"):
                    if ((entryData != 'TRUE') and (entryData != 'FALSE')):
                        JANUS_SER.sendUART("IGNITION not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.IGNITION) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.IGNITION = entryData
                elif (entryType == "SLED"):
                    if ((entryData != 'ON') and (entryData != 'OFF')):
                        JANUS_SER.sendUART("SLED not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.SLED) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.SLED = entryData
                elif (entryType == "ULED"):
                    if ((entryData != 'ON') and (entryData != 'OFF')):
                        JANUS_SER.sendUART("ULED not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.ULED) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.ULED = entryData
                elif (entryType == "AUTOON"):
                    if ((entryData != 'ON') and (entryData != 'OFF')):
                        JANUS_SER.sendUART("AUTOON not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.AUTOON) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.AUTOON = entryData
                elif (entryType == "IGNITIONFOLLOW"):
                    if ((entryData != 'TRUE') and (entryData != 'FALSE')):
                        JANUS_SER.sendUART("IGNITIONFOLLOW not valid: " + str(entryData) + "\r\n")
                        JANUS_SER.sendUART("Using Default Value: " + str(Config.IGNITIONFOLLOW) + "\r\n")
                    else:
                        #Passes, use the value
                        Config.IGNITIONFOLLOW = entryData   
                else:
                    JANUS_SER.sendUART("Unrecognized Entry, Not Set: " + str(entryType) + "\r\n")

            tmpReturn = 0
        else:
            tmpReturn = 1

    except:
        printException("String2Class")
        JANUS_SER.sendUART("String2Class exception. \r\n")  


    return tmpReturn



def FillDefault():
    #Fills out the default list from the user entered information below.
    # Input Parameter Definitions
    #   None
    #
    #   Returns:
    #    0: Pass
    #   -1: Exception

    
    tmpReturn = -1

    try:
##############################################################################################
##Begin User Entered Values
##############################################################################################

        ## BAND
        ## Please refer to AT Command guide for AT#BND
        ## If Terminal used in North America (BAND = '3')
        DefaultConfig.BAND = '3'

        ## NETWORK
        ## If Terminal used on ATT / Cingular in North America (NETWORK = 'ATT')
        ## Else (NETWORK = 'GSM')
        DefaultConfig.NETWORK = 'ATT'

        ## APN
        ## Gateway Address for GPRS traffic
        ## This setting is GSM Provider and possible customer specific when a VPN is used
        ## This demo is defaulted with 'internet' that is used for ATT wireless settings from pre-Cingular days
        ## You MUST obtain the APN setting for your GSM account.  Please call GSM provider!  Janus can't help you with this.
        DefaultConfig.APN = 'gprs02.motient.net'

        ## IP
        ## IP address of server on the Internet which Terminus will connect to send and receive data
        ## Address in this example is not operational for customer evaluation.  Customer must have their own server
        ## setup to interact with this demo.
        ## IP = 'xxx.xxx.xxx.xxx'
        DefaultConfig.IP = '12.237.120.180'

        ## PORT
        ## PORT number of server on the Internet which Terminus will connect to send and receive data
        ## PORT number in this example is not operational for customer evaluation.  Customer must have their own server
        ## setup to interact with this demo.
        DefaultConfig.PORT = '7777'

        ## PROTOCOL
        ## If customer is using TCPIP (PROTOCOL = 'TCPIP')
        ## Else leave blank (PROTOCOL = '')
        DefaultConfig.PROTOCOL = 'UDP'

        ## GPRS USER NAME
        ## If GSM Provider requires GPRS User Name (USERNAME = 'JOE')
        ## Else leave blank (USERNAME = '')
        DefaultConfig.USERNAME = ''

        ## GPRS PASSWORD
        ## If GSM Provider requires GPRS Password (PASSWORD = 'JOE123')
        ## Else leave blank (PASSWORD = '')
        DefaultConfig.PASSWORD = ''

        ## SMS_ENABLED
        ## SMS Enabled? (SMS_ENABLED = 'TRUE' or 'FALSE')
        DefaultConfig.SMS_ENABLED = 'TRUE'

        ## SMS
        ## SMS Designation phone number (SMS = '+16305551212')
        ## Although this number is put into the settings and checked for validity when pulled in from the configuration file, it's not used.
        ## For simplicity, the SMS functions of this demo take the incoming SMS and parse the originating phone number, replying to that phone number.
        DefaultConfig.SMS = '+16305551212'

        ## INTERVAL
        ## How many seconds the demo will wait before sending new GPS data to server. Valid range is 1 to 86400
        ## In this demo, GPS data will be sent every 10 seconds (INTERVAL = '10')
        DefaultConfig.INTERVAL = '10'

        ## Antenna LNA
        ## Does the external antenna have an LNA that needs to be powered, meaning is it an active antenna (bias voltage supplied by the tracker)?
        ## If the antenna is not an active type, enter 'FALSE', otherwise 'TRUE'
        DefaultConfig.LNA = 'TRUE'

        ## Switch Input
        ## Are we utilizing the input N/O switch?
        ## If we are going to use/monitor the switch, enter 'TRUE', otherwise 'FALSE'
        DefaultConfig.NOSWITCH = 'TRUE'

        ## Ignition Input
        ## Are we utilizing the Ignition input?
        ## If we are going to use/monitor the ignition, enter 'TRUE', otherwise 'FALSE'
        DefaultConfig.IGNITION = 'TRUE'

        ## Cellular Stat LED
        ## Do we want it active, or not?
        ## If we are going to have it active, enter 'ON', otherwise 'OFF'
        DefaultConfig.SLED = 'ON'

        ## GPS/User LED
        ## Do we want it active, or not?
        ## If we are going to have it active, enter 'ON', otherwise 'OFF'
        DefaultConfig.ULED = 'ON'

        ## Auto-On Control
        ## Do we want it active, or not?
        ## If we are going to have it active, enter 'ON', otherwise 'OFF'
        DefaultConfig.AUTOON = 'OFF'

        ## Ignition Follow Control
        ## This flag controls if we will be following the ignition signal for being on and reporting.
        ## If this is set, the unit will continue to report until the Ignition line becomes inactive.
        ## At that point, it will send a final report showing this, and then shut down.
        ## Note that this should only be used if AUTOON is OFF, otherwise the unit will just continue to
        ## automatically power up and power down if the ignition signal is inactive (car/truck is off).
        ## This is useful for power savings also, since the unit will be idle until it's needed,
        ## drawing minimal current from the battery.
        ## If we are going to have it active, enter 'TRUE', otherwise 'FALSE'
        DefaultConfig.IGNITIONFOLLOW = 'TRUE'


##############################################################################################
##End User Entered Values
##############################################################################################


        #Now we fill the "Config" class with the default values to initialize the class. All the data will be updated from the configuration file when List2Class is run.
        #However, in the case that the configuration file becomes corrupt, unreadable, or doesn't contain valid data, the default values shall be used.
        Config.BAND = DefaultConfig.BAND
        Config.NETWORK = DefaultConfig.NETWORK
        Config.APN = DefaultConfig.APN
        Config.IP = DefaultConfig.IP
        Config.PORT = DefaultConfig.PORT
        Config.PROTOCOL = DefaultConfig.PROTOCOL
        Config.USERNAME = DefaultConfig.USERNAME
        Config.PASSWORD = DefaultConfig.PASSWORD
        Config.SMS_ENABLED = DefaultConfig.SMS_ENABLED
        Config.SMS = DefaultConfig.SMS
        Config.INTERVAL = DefaultConfig.INTERVAL
        Config.LNA = DefaultConfig.LNA
        Config.NOSWITCH = DefaultConfig.NOSWITCH
        Config.IGNITION = DefaultConfig.IGNITION
        Config.SLED = DefaultConfig.SLED
        Config.ULED = DefaultConfig.ULED
        Config.AUTOON = DefaultConfig.AUTOON
        Config.IGNITIONFOLLOW = DefaultConfig.IGNITIONFOLLOW

        tmpReturn = 0


    except:
        printException("FillDefault")
        JANUS_SER.sendUART("FillDefault exception. \r\n")  


    return tmpReturn   



def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> JANUS_CONFIG"
    print "METHOD -> " + methodName

    return 