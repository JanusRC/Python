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

import GPIO         #code owned by: Telit
import MOD          #code owned by: Telit
import timers       #code owned by: Telit

import ATC          #code owned by: Janus Remote Communications
import JANUS_SER    #code owned by: Janus Remote Communications

##------------------------------------------------------------------------------------------------------------------
## Release  Information:
##  V1.0 (Clayton W. Knight, )   :   Initial release
##------------------------------------------------------------------------------------------------------------------

def init(inSLED):
    # This function initializes the IO
    #   Arguments:
    #   inSLED : Stat LED. Pass in either 'ON' or 'OFF'
    #       OFF - LED always OFF
    #       ON - LED follows registration status
    #   
    #
    #   Returns:
    #    0: Pass
    #   -1: Exception

    #GPIO Connections:
    #    1 - Do not utilize (Required by GPS)
    #    2 - IGNITION, LOW when ignition is active
    #    3 - N/O Switch, HIGH when the switch is closed
    #    4 - Do not utilize (Required by GPS)
    #    5 - GPS LED (User LED)
    #    6 - Auto ON Control, pulse HIGH to toggle the MCU's operative state. use GPIO1 to verify the state
    #    7 - IIC SDA : Utilizing this as Wake up Event Ignition Flag. Pulled high externally
    #    8 - IIC SCL : Utilizing this as Wake up Event N/O Switch Flag. Pulled high externally
    #    9 - GPIO1 : Utilizing this for Auto-On Verification FROM the MCU, 1 for auto-on enabled, 0 for auto-on disabled
    #    10 - GPIO2 : Utilizing this for Wake up Event verification TO the MCU, 1 if Event has been seen/recorded, otherwise 0.

    
    tmpReturn = -1

    try:
        
        #Set Stat LED to default value, 0 for OFF, 2 for ON
        if (inSLED == 'ON'):
            res = GPIO.setSLED(2, 10, 90)
        else:
            res = GPIO.setSLED(0, 10, 90)

        if (res == -1): #Errored out, 1 if no error -1 if error
            return tmpReturn
        
        #Now set all used GPIO to proper states.
        #GPIO.setIOvalue(GPIOnumber, value)
        #We do not need the above command, setIODir works best for this.
        #GPIO.setIOdir(number, value, direction)
        
        a = GPIO.setIOdir(2, 0, 0)  #Input
        b = GPIO.setIOdir(3, 0, 0)  #Input
        c = GPIO.setIOdir(5, 0, 1)  #Output, LOW (LED OFF)
        d = GPIO.setIOdir(6, 1, 0)  #Output, LOW (Auto-on OFF during INIT, taken care of in the command flow)
        e = GPIO.setIOdir(7, 0, 0)  #Input
        f = GPIO.setIOdir(8, 0, 0)  #Input
        g = GPIO.setIOdir(9, 0, 0)  #Input
        h = GPIO.setIOdir(10, 0, 1)  #Output, LOW (Wake up Event verification default sate, event NOT found)

        if (    a == -1
            or b == -1
            or c == -1
            or d == -1
            or e == -1
            or f == -1
            or g == -1
            or h == -1
            ):
            return tmpReturn    #Errored out, 1 if no error -1 if error
            

        tmpReturn = 0        

    except:
        printException("IO_init")
        JANUS_SER.sendUART("IO Init exception. \r\n")  


    return tmpReturn

def Cellular_LED(inSLED):
    # This function sets the cellular LED
    #   Arguments:
    #   inStatus : GPS LED status. Pass in either 'ON' or 'OFF'
    #       OFF - LED always OFF
    #       ON - LED function ON
    #
    #   Returns:
    #    0: Pass
    #   -1: Exception
    
    tmpReturn = -1

    try:
        
        #Set Stat LED to default value, 0 for OFF, 2 for ON
        if (inSLED == 'ON'):
            res = GPIO.setSLED(2, 10, 90)
        else:
            res = GPIO.setSLED(0, 10, 90)

        res = ATC.sendAtCmd('AT#SLEDSAV',ATC.properties.CMD_TERMINATOR,0,20)
        if (res == -1): #Errored out, 1 if no error -1 if error
            return tmpReturn
            

        tmpReturn = 0        

    except:
        printException("Cellular_LED")
        JANUS_SER.sendUART("GPS LED exception. \r\n")  


    return tmpReturn

def GPS_LED(inStatus, inActive):
    # This function initializes the IO
    #   Arguments:
    #   inStatus : GPS LED status. Pass in either 'ON' or 'OFF'
    #       OFF - LED always OFF
    #       ON - LED always ON
    #   inActive : GPS LED Usage. Pass in either 'ON' or 'OFF'
    #       OFF - LED is not used, ignore LED commands
    #       ON - LED is used, allow LED commands
    #
    #   Returns:
    #    0: Pass
    #   -1: Exception

    if (inActive == 'OFF'): #We are not using the LED, permanently turn it off and return as passing
        res = GPIO.setIOvalue(5, 0)
        return 0
    
    tmpReturn = -1

    try:
        
        #GPIO.setIOvalue(GPIOnumber, value)
        #    5 - GPS LED (User LED)
        if (inStatus == 'OFF'):
            res = GPIO.setIOvalue(5, 0)
        elif (inStatus == 'ON'):
            res = GPIO.setIOvalue(5, 1)

            
        if (res == -1):
            return tmpReturn    #Errored out, 1 if no error -1 if error
            

        tmpReturn = 0        

    except:
        printException("GPS_LED")
        JANUS_SER.sendUART("GPS LED exception. \r\n")  


    return tmpReturn

##def SW_IGN_Status(inSelection):
##    # This function reads the status of the event triggers based on the argument
##    #   Arguments:
##    #   inSelection - Select which I/O to read, accepts 'SWITCH' or 'IGN'
##    #
##    #   Returns:
##    #    0: Pass, Input LOW
##    #    1: Pass, Input HIGH
##    #   -1: Exception
##    
##    tmpReturn = -1
##
##    try:        
##        
##        #GPIO.getIOvalue(GPIOnumber)
##        #    2 - IGNITION
##        #    3 - N/O Switch
##        
##        if (inSelection == 'SWITCH'):
##            res = GPIO.getIOvalue(3)
##        elif (inSelection == 'IGN'):
##            res = GPIO.getIOvalue(2)
##
##            
##        if (res == -1):
##            return tmpReturn    #Errored out, 1 if no error -1 if error
##
##    except:
##        printException("SW_IGN Exception")
##        JANUS_SER.sendUART("SW_IGN Exception \r\n")  
##
##    #Return value of GPIO get
##    return res

def SW_IGN_Status():
    # This function reads the status of the event triggers, then toggles GPIO2 in response to signal the MCU that we received the information.
    # We are reading the MCU's signaling because it can poll and latch the states more accurately than directly reading in the python flow.
    # This allows less errors when reading the states in real time as well as catching a wake up event.
    #   Arguments:
    #   none
    #
    #   Returns:
    #    0: Pass, Switch is triggered
    #    1: Pass, Ignition is triggered
    #    2: Pass, BOTH are triggered
    #   -1: Exception
    #   -2: Pass, Neither is triggered
    
    tmpReturn = -1

    try:        
        
        #GPIO.getIOvalue(GPIOnumber)
        #    7 - IIC SDA/IGNITION : Utilizing this as Event Ignition Flag, active LOW
        #    8 - IIC SCL/SWITCH : Utilizing this as Event N/O Switch Flag, active LOW

        #GPIO.setIOvalue(GPIOnumber, value)      
        #    10 - GPIO2 : Utilizing this as the event received verification, active HIGH
        
        IgnRead = GPIO.getIOvalue(7)        
        SwitchRead = GPIO.getIOvalue(8) 

        if (IgnRead == 0 and SwitchRead == 1):  #Ignition Active, based on signal from MCU
            res = GPIO.setIOvalue(10, 1)
            tmpReturn = 1
        elif (IgnRead == 1 and SwitchRead == 0): #Switch Active, based on signal from MCU
            res = GPIO.setIOvalue(10, 1)
            tmpReturn = 0
        elif (IgnRead == 0 and SwitchRead == 0): #Both Active, based on signal from MCU
            res = GPIO.setIOvalue(10, 1)
            tmpReturn = 2
        elif (IgnRead == 1 and SwitchRead == 1): #Neither Active, based on signal from MCU
            tmpReturn = -2

        if (tmpReturn != -1):
            res = GPIO.setIOvalue(10, 0) #Reset the GPIO signaling


    except:
        printException("SW_IGN Exception")
        JANUS_SER.sendUART("SW_IGN Exception \r\n")  

    #Return value of GPIO get
    return tmpReturn

def AutoONControl(inCommand, inSelection):
    # This function sends a signal to MCU to tell it whether or not to handle Auto On,
    # waits for response on GPIO1 to verify the MCU is in the proper state.
    #   Arguments:
    #   inCommand - Select what to do, enter 'READ' or 'SET'.
    #       READ - Checks the MCU signal to verify the mode
    #       SET - Utilizes inSelection to change the mode.
    #   inSelection - Select to have the MCU run Auto-On or not, enter 'ON' or 'OFF.
    #       OFF - Auto-On is Disabled
    #       ON - Auto-On is Enabled
    #
    #   Returns:
    #       InCommand: READ
    #           0: Pass, Auto-on OFF
    #           1: Pass, Auto-on ON
    #           -1: Exception
    #           -2: Time out
    #       InCommand: SET
    #           0: Pass, Auto-on OFF
    #           1: Pass, Auto-on ON
    #           -1: Exception
    #           -2: Time out
    
    tmpReturn = -1

    try:        
        
        #GPIO.getIOvalue(GPIOnumber)
        #MOD.sleep(20) #Delay 
        #    9 - GPIO1 : Used as MCU signal verification
        
        if (inCommand == 'READ'):
            res = GPIO.getIOvalue(9)
            return res

        #GPIO.setIOvalue(GPIOnumber, value)
        #    6 - Auto ON Control
        #    9 - GPIO1 : Used as MCU signal verification
        if (inSelection == 'ON'): 
            res = GPIO.setIOvalue(6, 1)

            #Set a Timer for a quick loop to verify, we do this because it's a "just in case" breakout as opposed to a simple delay and check.
            timerA = timers.timer(0)
            timerA.start(5)    #5 seconds is MORE than enough.

            IoVal = GPIO.getIOvalue(9)
            #JANUS_SER.sendUART("Value from MCU: " + str(IoVal) + "\r\n")
            
            while (IoVal != 1):
                IoVal = GPIO.getIOvalue(9)
                if timerA.isexpired():
                    return (-2) #Time out while finding the signal


            res = GPIO.setIOvalue(6, 0) #End the HIGH pulse, MCU only toggles on a high signal
            return IoVal #Return the read value          
                
        elif (inSelection == 'OFF'):
            res = GPIO.setIOvalue(6, 1)

            #Set a Timer for a quick loop to verify, we do this because it's a "just in case" breakout as opposed to a simple delay and check.
            timerA = timers.timer(0)
            timerA.start(5)    #5 seconds is MORE than enough.

            IoVal = GPIO.getIOvalue(9)
            JANUS_SER.sendUART("Value from MCU: " + str(IoVal) + "\r\n")
            
            while (IoVal != 0):
                IoVal = GPIO.getIOvalue(9)
                if timerA.isexpired():
                    return (-2) #Time out while finding the signal


            res = GPIO.setIOvalue(6, 0) #End the HIGH pulse, MCU only toggles on a high signal  
            return IoVal #Return the read value


    except:
        printException("SW_IGN Exception")
        JANUS_SER.sendUART("SW_IGN Exception \r\n")  

    #Return Error value
    return tmpReturn


def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> JANUS_IO"
    print "METHOD -> " + methodName

    return 