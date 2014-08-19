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
##      DEBUG_CF.py
##  REVISION HISTORY:
##      1.0   04/22/2011  TWH --  Init Release
##

import sys              #code owned by: Telit
import SER              #code owned by: Telit

def init (speed,format):

    # Method return value:
    #   -2 = Unknown error occurred
    #   -1 = Exception occurred
    #    0 = Finished w/o error

    tmpReturn = -1

    try:

        #Init Serial Port Settings
        res = SER.set_speed(speed,format)
        if not(res == 1):
            return -2

    except:
        printException("init()")
        tmpReturn = -1

    return tmpReturn

def sendMsg(inSTR1, RUN_MODE):
# This function sends a debug message to print statement or DB9 Serial Port 

    # Input Parameter Definitions
    #   inSTR1: Debug Message
    #   RUN_MODE:
    #       (0) Send message via print statement "Script running in IDE"
    #       (1) Send message via DB9 serial port "Script running in Telit module"
    
    try:

        if (RUN_MODE):
            SER.send(inSTR1)
        else:
            print inSTR1
            
    except:
        printException("sendMsg()")

    return

def CLS(RUN_MODE):
# This function sends a VT100 Terminal Clear screen message to DB9 Serial Port 

    # Input Parameter Definitions
    #   RUN_MODE:
    #       (0) Don't send clear screen message
    #       (1) Send VT100 clear screen message via DB9 serial port "Script running in Telit module"
    
    try:

        if (RUN_MODE):
            SER.send("\033[2J\r")   #Clear screen
            SER.send("\033[H\r")   #Move cursor to home position        
            
    except:
        printException("CLS()")

    return

def printException(methodName):

    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> DEBUG_CF"
    print "METHOD -> " + methodName
        
    return