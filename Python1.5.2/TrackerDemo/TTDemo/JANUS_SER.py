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

import MDM      #code owned by: Telit
import MOD      #code owned by: Telit
import SER      #code owned by: Telit
import GPIO     #code owned by: Telit
import timers   #code owned by: Telit
import sys      #code owned by: Telit

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Thomas W. Heck, 05/19/2010)   :   Initial release
##------------------------------------------------------------------------------------------------------------------

def init(speed,format):
    # This function initializes the SER interface, you MUST initialize the interface or no data will be usable in or out of the DTE interface.

    try:


        #Init Serial Port Settings
        res = SER.set_speed(speed,format)
        if (res == -1):
            return(-1)

    except:
        printException("init_parameters(" + speed + "," + format + ")")
        return(-1)

    return (0)


def readUART():
    # This function receives data from the DTE

    try:

        res = ''
        res = SER.read()

    except:
        printException("readUART()")

    return(res)

def sendUART(inSTR):
    # This function data out to the DTE

    try:

        res = ''
        res = SER.send(str(inSTR))

    except:
        printException("sendUART()")
        
    return(res)

def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> JANUS_SER"
    print "METHOD -> " + methodName

    return 