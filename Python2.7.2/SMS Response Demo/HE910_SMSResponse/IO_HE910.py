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

import GPIO         
import sys

import ATC_HE910 as myATC

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Clayton W. Knight, )   :   Initial release
##------------------------------------------------------------------------------------------------------------------

def init():
    # This function initializes the IO
    #   Arguments:
    #   None
    #
    
    
    #GPIO Connections:
    #    1 - Cellular LED
    #    2 - GPS LED (User LED)

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        
        #Now set all used GPIO to proper states.
        #GPIO.setIOvalue(GPIOnumber, value)
        #We do not need the above command, setIODir works best for this.
        #GPIO.setIOdir(number, value, direction)
        
        a = GPIO.setIOdir(1, 0, 2)  #Output, Alternate Function
        b = GPIO.setIOdir(2, 0, 1)  #Output, LOW (LED OFF)

        if (    a == -1
            or b == -1
            ):
            return rtnList    #Errored out
            

        rtnList[0] = 0  #no error, no data  

    except:
        print sys.exc_info()
        rtnList[0] = -1


    return rtnList

def Cellular_LED(inSLED):
    # This function sets the cellular LED
    #   Arguments:
    #   inStatus : GPS LED status. Pass in either 'ON' or 'OFF'
    #       OFF - LED always OFF
    #       ON - LED function ON
    #


    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data        
        
        #Set Stat LED to default value, 0 for OFF, 2 for ON
        if (inSLED == 'ON'):
            rtnList[1] = GPIO.setSLED(2, 10, 90)
        else:
            rtnList[1] = GPIO.setSLED(0, 10, 90)

        if (rtnList[1] == -1): #Errored out
            return rtnList            

        rtnList = myATC.sendAtCmd('AT#SLEDSAV',myATC.properties.CMD_TERMINATOR,0,20)
        if (rtnList[1] == -1): #Errored out
            return rtnList
            

        rtnList[0] = 0  #no error, no data  

    except:
        print sys.exc_info()
        rtnList[0] = -1


    return rtnList

def USER_LED(inStatus):
    # This function initializes the IO
    #   Arguments:
    #   inStatus : GPS LED status. Pass in either 'ON' or 'OFF'
    #       OFF - LED always OFF
    #       ON - LED always ON
    #
    

    try:

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        
        #GPIO.setIOvalue(GPIOnumber, value)
        #    2 - GPS LED (User LED)
        
        if (inStatus == 'OFF'):
            rtnList[1] = GPIO.setIOvalue(2, 0)  #Output, LOW (LED OFF)
        elif (inStatus == 'ON'):
            rtnList[1] = GPIO.setIOvalue(2, 1)  #Output, HIGH (LED ON)

            
        if (rtnList[1] == -1): #Errored out
            return rtnList    


        rtnList[0] = 0  #no error, no data       

    except:
        print sys.exc_info()
        rtnList[0] = -1 


    return rtnList

