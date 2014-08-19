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

import ATC          #code owned by: Janus Remote Communications
import JANUS_SER    #code owned by: Janus Remote Communications

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Clayton W. Knight, )   :   Initial release
##------------------------------------------------------------------------------------------------------------------

def init(LNA_Arg):
    # This function initializes the GPS
    #   Arguments:
    #   LNA_Arg: External LNA? TRUE or FALSE
    #
    #   Returns:
    #    0: Pass
    #   -1: Exception
    #   -2: AT command ERROR
    
    tmpReturn = -1

    try:

        res = ATC.sendAtCmd("AT$GPSD?",ATC.properties.CMD_TERMINATOR,0,2)           #query if the modem is in "controlled" mode, required for this tracking unit.
        if (res != "$GPSD: 2"):
            res = ATC.sendAtCmd('AT$GPSD=2',ATC.properties.CMD_TERMINATOR,0,2)      #If it's not set, set it.

        #Check if the GPS command failed out
        if (res=='ERROR'):
            return (-2)        

        if (LNA_Arg == 'TRUE'):                                                     #Query if we have an active GPS antenna with powered LNA
            res = ATC.sendAtCmd('AT$GPSAT=1',ATC.properties.CMD_TERMINATOR,0,2)     #We do, so turn OFF the internal LNA to avoid oversaturation.
        else:
            res = ATC.sendAtCmd('AT$GPSAT=0',ATC.properties.CMD_TERMINATOR,0,2)     #We do not, it's passive, so turn ON the internal LNA

        #Check if the GPS command failed out
        if (res=='ERROR'):
            return (-2) 

        #Turn the GPS ON
        GPS.powerOnOff(1)

        #No errors
        tmpReturn = 0      

    except:
        printException("GPS_Init")
        JANUS_SER.sendUART("GPS Init exception. \r\n")  


    return tmpReturn




def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> JANUS_GPS"
    print "METHOD -> " + methodName

    return 