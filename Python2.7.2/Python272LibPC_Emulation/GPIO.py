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
import time
import MDM

def setIOvalue(GPIOnumber, value):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#GPIO=')
    MDM.mdmser.write(str(GPIOnumber))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(value))
    MDM.mdmser.write(',1\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      result = 1
    else:
      result = -1
  else:
    print 'dummy setIOvalue('+str(GPIOnumber)+','+str(value)+')'
    result = 1
  return result

def getIOvalue(GPIOnumber):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#GPIO=')
    MDM.mdmser.write(str(GPIOnumber))
    MDM.mdmser.write(',2\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      commaPos = data.find(',')
      stat = data[commaPos+1]
      result = int(stat)
    else:
      result = -1
  else:
    print 'dummy getIOvalue('+str(GPIOnumber)+')'
    result = 1
  return result

def setIOdir(GPIOnumber, value, dir):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#GPIO=')
    MDM.mdmser.write(str(GPIOnumber))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(value))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(dir))
    MDM.mdmser.write('\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      result = 1
    else:
      result = -1
  else:
    print 'dummy setIOdir('+str(GPIOnumber)+','+str(value)+','+str(dir)+')'
    result = 1
  return result

def getIOdir(GPIOnumber):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#GPIO=')
    MDM.mdmser.write(str(GPIOnumber))
    MDM.mdmser.write(',2\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      commaPos = data.find(',')
      stat = data[commaPos-1]
      result = int(stat)
    else:
      result = -1
  else:
    print 'dummy getIOdir('+str(GPIOnumber)+')'
    result = 1
  return result

def setDAC(enable, value):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#DAC=')
    MDM.mdmser.write(str(enable))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(value))
    MDM.mdmser.write('\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      result = 1
    else:
      result = -1
  else:
    print 'dummy setDAC('+str(enable)+','+str(value)+')'
    result = 1
  return result

def getADC(ADCnumber):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#ADC=')
    MDM.mdmser.write(str(ADCnumber))
    MDM.mdmser.write(',2,0\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      colonPos = data.find(': ')
      data1 = data[colonPos+2 : ]
      crPos = data1.find('\r')
      value = data1[ : crPos]
      result = int(value)
    else:
      result = -1
  else:
    print 'dummy getADC('+str(ADCnumber)+')'
    result = 1
  return result

def setVAUX(VAUXnumber, value):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#VAUX=')
    MDM.mdmser.write(str(VAUXnumber))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(value))
    MDM.mdmser.write('\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      result = 1
    else:
      result = -1
  else:
    print 'dummy setVAUX('+str(VAUXnumber)+','+str(value)+')'
    result = 1
  return result

def setSLED(status, onTime, offTime):
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#SLED=')
    MDM.mdmser.write(str(status))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(onTime))
    MDM.mdmser.write(',')
    MDM.mdmser.write(str(offTime))
    MDM.mdmser.write('\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      result = 1
    else:
      result = -1
  else:
    print 'dummy setSLED('+str(status)+','+str(onTime)+','+str(offTime)+')'
    result = 1
  return result

def getCBC():
  global MDM
  if MDM.mdmser.getCD() == False:
    MDM.mdmser.write('AT#CBC\r')
    data = ''
    timeMax = time.time() + 5.0
    while data.find('OK\r') == -1 and data.find('ERROR\r') == -1 and time.time() < timeMax:
      data = data +  MDM.mdmser.read(100)
    if data.find('OK\r') != -1:
      commaPos = data.find(',')
      stat = data[commaPos-1]
      data1 = data[commaPos+1 : ]
      crPos = data1.find('\r')
      value = data1[ : crPos]
      result = (int(stat),int(value))
    else:
      result = -1
  else:
    print 'dummy getCBC()'
    result = 1
  return result
