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


## Written By Thomas W. Heck
##  MODULE:
##      GPRS.py
##  REVISION HISTORY:
##      2.0     05/18/2010  TWH --  Init Release
##

import MDM              #code owned by: Telit
import MOD              #code owned by: Telit
import timers           #code owned by: Telit
import sys              #code owned by: Telit

import ATC              #code owned by: Janus Remote Communications
import JANUS_SER        #code owned by: Janus Remote Communications

class properties:
    CMD_BUFFER = ''
################################################################################################
## Methods for handling GPRS communication
################################################################################################
    
def init(PDPindex,APN):

    try:

        #Define GPRS Settings, MUST change APN String in script for your Carrier Specific setting
        res = ATC.sendAtCmd('AT+CGDCONT=' + str(PDPindex) + ',"IP","' + str(APN) + '","0.0.0.0",0,0' ,ATC.properties.CMD_TERMINATOR,0,20)
        #How long does system wait before sending undersized packet measured in 100ms settings
        res = ATC.sendAtCmd('AT#DSTO=10' ,ATC.properties.CMD_TERMINATOR,0,20)

        #Define Min/required Quality of Service
        res = ATC.sendAtCmd('AT+CGQMIN=1,0,0,0,0,0' ,ATC.properties.CMD_TERMINATOR,0,20)
        res = ATC.sendAtCmd('AT+CGQREQ=1,0,0,3,0,0' ,ATC.properties.CMD_TERMINATOR,0,20)

        #escape guard time, after set time escape sequence is accepted, set in 20ms settings
        res = ATC.sendAtCmd('ATS12=40' ,ATC.properties.CMD_TERMINATOR,0,20)

        #disable the escape sequence from transmitting during a data session
        res = ATC.sendAtCmd('AT#SKIPESC=1' ,ATC.properties.CMD_TERMINATOR,0,20)

        #Set connect timeOuts and packet sizes for PDP#1 and Socket#1
        res = ATC.sendAtCmd('AT#SCFG=1,1,1500,600,100,10' ,ATC.properties.CMD_TERMINATOR,0,20)

        #Sets the behavior of #SSEND and #SREVC, Socket#1
        res = ATC.sendAtCmd('AT#SCFGEXT=1,2,0,30,0,0' ,ATC.properties.CMD_TERMINATOR,0,20)

    except:
        printException("initGPRS(" + PDPindex + "," + APN + ")")

    return    

def openSocket(addr,port,sockNum,userID,userPassword,protocol,connMode):
    #Function Open a socket and responds with CONNECT/NO CARRIER/ERROR
    #   Arguments:
    #   addr: IP Address
    #   port: Port of the address
    #   sockNum: Socket number
    #   userID: User ID
    #   userPassword: User Password
    #   protocol: TCPIP or UDP
    #   connMode: 0 for Command Mode, 1 for Online Mode
    #
    #   Returns:
    #    0: Pass
    #   -1: Exception
    #   -2: AT command ERROR

    tmpReturn = -1
    
    try:
        #Close Socket
        res = ATC.sendAtCmd('AT#SS',ATC.properties.CMD_TERMINATOR,0,20)
        if (res!="#SS: 1,0"):
            res = ATC.sendAtCmd('AT#SH=1',ATC.properties.CMD_TERMINATOR,0,20)

        if (res=='ERROR'):
            return (-2)
        
        #Activate PDP if needed  
        res = ATC.sendAtCmd('AT#SGACT?',ATC.properties.CMD_TERMINATOR,0,20) 
        if (res!="#SGACT: 1,1"):
            delaySec(1)
            res = ATC.sendAtCmd('AT#SGACT=1,1,"' + str(userID) + '","' + str(userPassword) + '"' ,ATC.properties.CMD_TERMINATOR,0,180) 

        if (res=='ERROR'):
            return (-2)           

        #Open Socket to Server in Command mode
        if (str(protocol)=='TCPIP'):
            res = ATC.sendAtCmd('AT#SD=' + str(sockNum) + ',0,' + str(port) + ',"' + str(addr) + '",0,0,' + str(connMode),ATC.properties.CMD_TERMINATOR,0,180) #You get an OK, not a CONNECT
        else:
            res = ATC.sendAtCmd('AT#SD=' + str(sockNum) + ',1,' + str(port) + ',"' + str(addr) + '",0,5559,' + str(connMode),ATC.properties.CMD_TERMINATOR,0,180)  #You get an OK, not a CONNECT

        if (res!='OK'):
            return (-2) 

        #Pass
        tmpReturn = 0
        
    except:
        printException("openSocket(" + str(addr) + "," + str(port) + "," + str(sockNum) + "," + str(userID) + "," + str(userPassword) + "," + str(protocol) + str(connMode) + ")")

    return tmpReturn

def send_CM(inSTR,connId,timeOut):
    # This function sends a string while in Command Mode
    #   Arguments:
    #   inSTR: String to send
    #   connId: Connection #
    #   timeOut: Amount of time alotted to send
    #
    #   Returns:
    #    0: Pass
    #    1: String argument empty
    #   -1: Exception
    #   -2: Timeout
    
    if (len(inSTR)==0):
        return 1

    try:

        res = MDM.send('AT#SSEND=' + str(connId) + '\r\n', 0)   

        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(timeOut)

        prompt = '\r\n> '

        #Start looking for '\r\n>'
        while(1):

            properties.CMD_BUFFER = properties.CMD_BUFFER + MDM.receive(1)      
            pos1 = properties.CMD_BUFFER.find(prompt)   #look for prompt characters
            if (pos1>=0):
                properties.CMD_BUFFER = properties.CMD_BUFFER[0:pos1] + properties.CMD_BUFFER[pos1+len(prompt):len(properties.CMD_BUFFER)]
                res = MDM.send(inSTR, 0)
                res = MDM.sendbyte(0x1a, 0)       
                
                tempread = ''
                res = ''
                while(1):
                    tempread = MDM.read()
                    if (tempread != ''):
                        res = res + tempread

                    if (res.find('OK')>=0):
                        return (0)    #Pass
                    
                    if timerA.isexpired():
                        return (-2)    #Expired, can't find OK response

            if timerA.isexpired():
                return (-2)    #Expired, no prompt found

    except:
        printException("send_CM(" + inSTR + "," + connId + "," + timeOut + ")")
        JANUS_SER.sendUART("Send CM Exception. \r\n")  

    #Would return with something else before this if it passes without exception
    return (-1) 



def closeSocket(sockNum):

    try:
        #Close Socket
        res = ATC.sendAtCmd('AT#SH=' + str(sockNum),ATC.properties.CMD_TERMINATOR,0,20)

    except:
        printException("closeSocket(" + sockNum + ")")

    return res

################################################################################################
## Misc support Methods
################################################################################################

def delaySec(seconds):

    try:

        if(seconds<=0): return    

        timerA = timers.timer(0)
        timerA.start(seconds)
        while 1:
            MOD.watchdogReset()
            if timerA.isexpired():
                break

    except:
        printException("delaySec(" + seconds + ")")

    return

def printException(methodName):
    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> GPRS"
    print "METHOD -> " + methodName

    return