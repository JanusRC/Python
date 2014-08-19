#Telit Extensions
#
#Copyright 2012, Telit Communications S.p.A.
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
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
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
#
import serial

#print "SER start"
freeser = serial.Serial('COM1', 115200, timeout=0, rtscts=0)

def send(string):
  global freeser
  freeser.write(string)
  result = 1
  return result

def sendavail():
  return 4096

def read():
  global freeser
  string = freeser.read(512)
  return string

def sendbyte(byte):
  global freeser
  string = chr(byte)
  freeser.write(string)
  result = 1
  return result

def readbyte():
  global freeser
  string = freeser.read(1)
  if string == '':
    result = -1
  else:
    result = ord(string)
  return result

def setDCD(dcd):
  global freeser
  if dcd == 0:
    print 'dummy setDCD(0)'
  else:
    print 'dummy setDCD(1)'
  return

def setCTS(cts):
  global freeser
  if cts == 0:
    print 'dummy setCTS(0)'
  else:
    print 'dummy setCTS(1)'
  return

def setDSR(dsr):
  global freeser
  if dsr == 0:
    print 'dummy setDSR(0)'
  else:
    print 'dummy setDSR(1)'
  return

def setRI(ri):
  global freeser
  if ri == 0:
    print 'dummy setRI(0)'
  else:
    print 'dummy setRI(1)'
  return

def getRTS():
  global freeser
  print 'dummy getRTS()'
  rts = False
  if rts == False:
    result = 0
  else:
    result = 1
  return result

def getDTR():
  global freeser
  print 'dummy getDTR()'
  dtr = False
  if dtr == False:
    result = 0
  else:
    result = 1
  return result

def set_speed(speed, format='8N1'):
  global freeser
  result = 1
  if speed == '300':
    freeser.setBaudrate(300)
  elif speed == '600':
    freeser.setBaudrate(600)
  elif speed == '1200':
    freeser.setBaudrate(1200)
  elif speed == '2400':
    freeser.setBaudrate(2400)
  elif speed == '4800':
    freeser.setBaudrate(4800)
  elif speed == '9600':
    freeser.setBaudrate(9600)
  elif speed == '19200':
    freeser.setBaudrate(19200)
  elif speed == '38400':
    freeser.setBaudrate(38400)
  elif speed == '57600':
    freeser.setBaudrate(57600)
  elif speed == '115200':
    freeser.setBaudrate(115200)
  else:
    result = -1
  if result == 1:
    if format == '8N1':
      freeser.bytesize = serial.EIGHTBITS
      freeser.parity = serial.PARITY_NONE
      freeser.stopbits = serial.STOPBITS_ONE
    elif format == '8N2':
      freeser.bytesize = serial.EIGHTBITS
      freeser.parity = serial.PARITY_NONE
      freeser.stopbits = serial.STOPBITS_TWO
    elif format == '8E1':
      freeser.bytesize = serial.EIGHTBITS
      freeser.parity = serial.PARITY_EVEN
      freeser.stopbits = serial.STOPBITS_ONE
    elif format == '8O1':
      freeser.bytesize = serial.EIGHTBITS
      freeser.parity = serial.PARITY_ODD
      freeser.stopbits = serial.STOPBITS_ONE
    elif format == '7N1':
      freeser.bytesize = serial.SEVENBITS
      freeser.parity = serial.PARITY_NONE
      freeser.stopbits = serial.STOPBITS_ONE
    elif format == '7N2':
      freeser.bytesize = serial.SEVENBITS
      freeser.parity = serial.PARITY_NONE
      freeser.stopbits = serial.STOPBITS_TWO
    elif format == '7E1':
      freeser.bytesize = serial.SEVENBITS
      freeser.parity = serial.PARITY_EVEN
      freeser.stopbits = serial.STOPBITS_ONE
    elif format == '7O1':
      freeser.bytesize = serial.SEVENBITS
      freeser.parity = serial.PARITY_ODD
      freeser.stopbits = serial.STOPBITS_ONE
    elif format == '8E2':
      freeser.bytesize = serial.EIGHTBITS
      freeser.parity = serial.PARITY_EVEN
      freeser.stopbits = serial.STOPBITS_TWO
    else:
      freeser.bytesize = serial.EIGHTBITS
      freeser.parity = serial.PARITY_NONE
      freeser.stopbits = serial.STOPBITS_ONE
  return result

