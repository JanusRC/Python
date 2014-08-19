#Telit Extensions
#
#Copyright © 2004, DAI Telecom S.p.A.
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
#

""" Telit - Python class timer - Example
This script is an example of a Python class based on MOD.secCounter()
method imported from MOD built-in module.
This class implements same basic functions needed to handle timers
in a GM862-PCS Python script.
start(seconds)
starts a timer counter with expiration time in seconds.
stop()
stops a timer counter.
isexpired()
returns 1 if timer counter is expired otherwise returns 0.
isrunning()
returns 1 if timer counter is running otherwise returns 0.
change(seconds)
changes a timer counter expiration time.
count()
returns actual timer counter in seconds.


The following is a simple example about how to use this class:

import timers
timerA = timers.timer(0)
timerA.start(15)
while 1:
  if timerA.isexpired():
    print 'timerA expired'
    break

"""

import MOD

class timer:

  def __init__(self, seconds):
    self.start(seconds)

  def start(self, seconds):
    self.startTime = MOD.secCounter()
    self.expirationTime = self.startTime + seconds
    if seconds != 0:
      self.running = 1
      self.expired = 0
    else:
      self.running = 0
      self.expired = 0

  def stop(self):
    self.running = 0
    self.expired = 0

  def isexpired(self):
    if self.running == 1:
      timeNow = MOD.secCounter()
      if timeNow > self.expirationTime:
        self.running = 0
        self.expired = 1
      else:
        self.expired = 0
    return self.expired

  def isrunning(self):
    if self.running == 1:
      timeNow = MOD.secCounter()
      if timeNow > self.expirationTime:
        self.running = 0
        self.expired = 1
      else:
        self.expired = 0
    return self.running

  def change(self, seconds):
    self.expirationTime = self.startTime + seconds

  def count(self):
    if self.running == 1:
      timeNow = MOD.secCounter()
      return (timeNow - self.startTime)
    else:
      return -1
 
