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

import time
import sys

import SER as mySER

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Thomas W. Heck, 05/19/2010)   :   Initial release
##------------------------------------------------------------------------------------------------------------------

def init(speed,format):
    # This function initializes the SER interface, you MUST initialize the interface or no data will be usable in or out of the DTE interface.

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data

        #Init Serial Port Settings
        rtnList[0] = mySER.set_speed(speed,format)
        if (rtnList[0] == -1):
            return rtnList

        rtnList[0] = 0   

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList


def readUART():
    # This function receives data from the DTE

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data        

        rtnList[1] = ''
        rtnList[1] = mySER.read()

        if (rtnList[1] == -1):
            return rtnList        
            
        rtnList[0] = 1  

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

def sendUART(inSTR):
    # This function data out to the DTE

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Timeout
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data  

        rtnList[1] = ''
        rtnList[1] = mySER.send(str(inSTR))

        if (rtnList[1] == -1):
            return rtnList

        rtnList[0] = 0          

    except:
        print sys.exc_info()
        rtnList[0] = -1

    return rtnList

