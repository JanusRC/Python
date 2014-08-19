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
##      GPRS.py
##  REVISION HISTORY:
##      1.0   09/16/2009  TWH --  Init Release
##      1.1   05/07/2010  TWH --    1.) Changed GPRS.init() to send TCPIP received data in HEXADECIMAL format
##                                  2.) Changed GPRS.parseSRING()to convert HEXADECIMAL data into binary
##      1.2   05/12/2010  TWH --    1.) Fixed bug in GPRS.parseSRING() that would drop characters.  GPRS.parseSRING()
##                                      now exits when the CMD_BUFFER doesn't have a complete SRING: response.  This allows
##                                      the remaining bytes on the MDM interface to be read and appended to the COMMAND_BUFFER.
##

import MDM              #code owned by: Telit
import MOD              #code owned by: Telit
import timers           #code owned by: Telit
import sys              #code owned by: Telit

import ATC              #code owned by: Janus Remote Communications

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

        #Set connect timeouts and packet sizes for PDP#1 and Socket#1
        res = ATC.sendAtCmd('AT#SCFG=1,1,1500,600,100,10' ,ATC.properties.CMD_TERMINATOR,0,20)

        #Sets the behavior of #SSEND and #SREVC, Socket#1
        res = ATC.sendAtCmd('AT#SCFGEXT=1,2,0,30,0,0' ,ATC.properties.CMD_TERMINATOR,0,20)

    except:
        printException("initGPRS()")

    return    

def openSocket(addr,port,sockNum,userID,userPassword,protocol,connMode):
    #Function Open a socket and responds with CONNECT/NO CARRIER/ERROR

    try:
        #Close Socket
        res = ATC.sendAtCmd('AT#SS',ATC.properties.CMD_TERMINATOR,0,20)
        if (res!="#SS: 1,0"):
            res = ATC.sendAtCmd('AT#SH=1',ATC.properties.CMD_TERMINATOR,0,20)

        if (res=='ERROR'):
            return
        
        #Activate PDP if needed  
        res = ATC.sendAtCmd('AT#SGACT?',ATC.properties.CMD_TERMINATOR,0,20) 
        if (res!="#SGACT: 1,1"):
            delaySec(1)
            res = ATC.sendAtCmd('AT#SGACT=1,1,"' + str(userID) + '","' + str(userPassword) + '"' ,ATC.properties.CMD_TERMINATOR,0,180) 

        if (res=='ERROR'):
            return            

        #Open Socket to Server
        if (str(protocol)=='TCPIP'):
                res = ATC.sendAtCmd('AT#SD=1,0,' + str(port) + ',"' + str(addr) + '",0,0,' + str(connMode),'OK\r\n',0,180)
        else:
            res = ATC.sendAtCmd('AT#SD=1,1,' + str(port) + ',"' + str(addr) + '",0,5559,' + str(connMode),'OK\r\n',0,180)

    except:
        printException("openSocket()")

    return res

def send_CM(inSTR,connId,timeOut):

## TWH - 09/16/2009
## Need to determine to timeout for this command

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

                res = ''
                tmpByte = -1
                while(1):
                    tmpByte = MDM.readbyte()
                    if (tmpByte != -1):
                        res = res + tmpByte

                    if (res.find('\r\nOK\r\n')>=0):
                        return 0
                    if timerA.isexpired():
                        return -2

            if timerA.isexpired():
                return -2

    except:
        printException("send_CM()")

    return -3

def parseSRING():

    syntaxFailed = 0

    pos1 = 0
    pos2 = 0
    pos3 = 0
    pos4 = 0
    pos5 = 0
    pos6 = 0
    lenData = 0
    sockNum = 0

    res = ''

    #find(s, sub[, start[,end]])
    try:

        print properties.CMD_BUFFER
        inData = properties.CMD_BUFFER
        
        # Has Data Arrived?
        pos1 = properties.CMD_BUFFER.find('SRING',0)
        if(pos1==-1):
            return res
        
        pos2 = properties.CMD_BUFFER.find(':',pos1+1)            
        if(pos2==-1):
            return res
        
        pos3 = properties.CMD_BUFFER.find(',',pos2+1)
        if(pos3==-1):
            return res
        
        #Store reported Socket Number
        try:
            sockNum = int(properties.CMD_BUFFER[pos2+1:pos3],10)
        except:
            syntaxfailed = 1

        pos4 = properties.CMD_BUFFER.find(',',pos3+1)
        if(pos4==-1):
            return res

        #Store reported Data length
        try:
            lenData = int(properties.CMD_BUFFER[pos3+1:pos4],10)
        except:
            syntaxFailed = 1
            
        pos5 = properties.CMD_BUFFER.find('\r\n',pos4+1)
        if(pos5==-1):
            return res
        
        # Is valid Socket Number? (1 - 6)
        if ((sockNum<1) and (sockNum>6)):
            syntaxFailed = 1            

        if ((not(pos2>pos1)) and (not(pos2<pos3)) and (not(pos3<pos4)) and (not(pos4<pos5))):
            syntaxFailed = 1

        # Is Data size correct?
        if (lenData != (pos5 - (pos4+1))):
            syntaxFailed = 1

        tmpRes = ''        
        if (syntaxFailed==0):
            res = properties.CMD_BUFFER[pos4+1:pos5]
            # remove SRING: from buffer and leading characters
            properties.CMD_BUFFER = properties.CMD_BUFFER[pos5+2:len(properties.CMD_BUFFER)]        

        else:
            pos6 = properties.CMD_BUFFER.find('SRING:',pos1+1)
            if (pos6>-1):
                # remove SRING: from buffer and leading characters
                properties.CMD_BUFFER = properties.CMD_BUFFER[pos6:len(properties.CMD_BUFFER)]
            else:
                properties.CMD_BUFFER = properties.CMD_BUFFER[pos1+5:len(properties.CMD_BUFFER)]
    except:
        printException("parseSRING()")
        res = ''

    return res

def exitDataMode():

    try:
        #Exit data mode

        ##Lookup the Escape Sequence Guard Time
        ## Future Use

        
        # Delay to meet Escape Sequence Guard Time
        ## Remove Hard Coded Escape Sequence Guard Time
        delaySec(1)
        
        #Start timeout counter        
        timerA = timers.timer(0)
        timerA.start(20)

        ##Lookup the Escape Sequence
        ## Future Use
        
        #Sending +++
        ## Remove Hard Coded Escape Sequence
        res = MDM.send('+++', 10)


        #Wait for response
        res = ''
        while ((res.find("OK")<=-1) and (res != 'timeOut')):
            MOD.watchdogReset()
            res = res + MDM.receive(50)

            pass            
            if timerA.isexpired():
                res = 'timeOut'

    except:
        printException("exitDataMode()")

    print res

    return res

def closeSocket(sockNum):

    try:
        #Close Socket
        res = ATC.sendAtCmd('AT#SH=' + str(sockNum),ATC.properties.CMD_TERMINATOR,0,20)

    except:
        printException("closeSocket()")

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
        printException("delaySec()")

    return

def printException(methodName):

    print "Script encountered an exception."
    print "Exception Type: " + str(sys.exc_type)
    print "MODULE -> GPRS"
    print "METHOD -> " + methodName

    return
