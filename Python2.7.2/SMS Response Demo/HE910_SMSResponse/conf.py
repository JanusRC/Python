##--------------------------------------------------------------------------------------
## Module: conf.py
## Release Information:
##  V1.0.0    (Thomas W. Heck, 09/24/2012)   :   Initial release
##--------------------------------------------------------------------------------------

##--------------------------------------------------------------------------------------
## NOTES
##  1.)  Works with the following T2 Products
##            HSPA910T2
##--------------------------------------------------------------------------------------

#Copyright 2012, Janus Remote Communications
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

class conf:
    '''
    Class used to read and write configuration options for the 400AP demonstrations
    '''

    ##Class properties
    ENS = ''
    APN = ''
    IP = ''
    PORT = ''
    PROTOCOL = ''
    USERNAME = ''
    PASSWORD = ''
    SMSD = ''
    INTERVAL = ''
    CGMM = ''
    CGMR = ''
    IMEI_MEID = ''
    GPS_PORT = ''
    GPS_BAUD = ''
    GPS_FORMAT = ''
    CONF_STATUS = ''

    ##Class methods
    def __init__(self, appPath, appFile):
        
        #Constructor
        
        # CONF_STATUS:
        #      0, Configuration Valid
        #     -1, Configuration invalid, Error occurred
        #     -2, Configuration invalid, Missing conf file
        #     -3, Configuration invalid, Undefined Parameters
        #     -4, Configuration invalid, Input Parameter out of range
        #     -5, Configuration invalid, Incorrect Number of Parameters
        #     -6, Configuration invalid, Unknown Telit radio
        #     -7, Configuration invalid, GPS serial unknown

        self.ENS = ''
        self.APN = ''
        self.IP = ''
        self.PORT = ''
        self.PROTOCOL = ''
        self.USERNAME = ''
        self.PASSWORD = ''
        self.SMSD = ''
        self.INTERVAL = ''
        self.CGMM = ''
        self.CGMR = ''
        self.GPS_PORT = ''
        self.GPS_BAUD = ''
        self.GPS_FORMAT = ''
        self.IMEI_MEID = ''
        self.CONF_STATUS = -1

        self.CONF_STATUS = self.read(appPath, appFile)
        if self.CONF_STATUS < 0:  return        

        return

    def read(self, appPath, appFile):
        ###########################################################################
        #Function Returns   -1, Function Failed
        #                   -2, No File Exists
        #                   -3, Undefined Parameters
        #                   -4, Input Parameter out of range
        #                   -5, Incorrect Number of Parameters
        #                    0, Defaults Loaded
        ###########################################################################

        res = -1
        #Load Application Settings
        
        # Open local text file with system parameter
        print 'opening: ' + appPath + '/' + appFile
        try: f = open(appPath + '/' + appFile,'r')
        except:
            return -2
        
        #Read in all configuration parameters
        try:
            line = ''
            for x in f:
                if len(x.strip()) > 0:
                    if x[0] == '#': pass
                    else: line += x.strip() + ','
            if len(line) > 0:
                line = line[0:len(line)-1]
                
        except:
            return -1
        
        #Close Opened File
        try: f.close()
        except:
            return -1
        
        #Parse and validate input parameters
        try:
            tmp_list = line.split(',')
            res = self.paramSyntax(tmp_list)
        except:
            return -1
        
        return res
            
    def write(self):
        return (-1)

    def paramSyntax(self, theList):
        ###########################################################################
        #Function Returns   -1, Function Failed
        #                   -2, Undefined
        #                   -3, Undefined Parameters
        #                   -4, Input Parameter out of range
        #                   -5, Incorrect Number of Parameters
        #                    0, Function completed without error
        ###########################################################################
        res = -1
        
        #Validate Input Parameters

        if (len(theList)==11):
            for x in theList:
                print x + "\r\n"
                line_list = x.split('=')
                if (line_list[0].strip() == 'CGMM'):
                    self.CGMM = line_list[1].strip()
                elif (line_list[0].strip() == 'CGMR'):
                    self.CGMR = line_list[1].strip()
                elif (line_list[0].strip() == 'ENS'):
                    self.ENS = line_list[1].strip()
                    #Verify ENS is a number between 0 and 1
                    try:
                        if ((int(self.ENS) < 0) or (int(self.ENS) > 1)):
                            #BAND is out of range
                            self.ENS = ''
                            return (-4)
                    except:
                        #BAND is not a valid integer
                        return (-4)
                elif (line_list[0].strip() == 'APN'):
                    self.APN = line_list[1].strip()
                elif (line_list[0].strip() == 'IP'):
                    self.IP = line_list[1].strip()
                    tmp_list = self.IP.split('.')
                    #Does IP address have 4 octets?
                    if (len(tmp_list)==4):
                        for y in tmp_list:
                            #Verify each octet is a number between 0 and 255
                            try:
                                if ((int(y) < 0) or (int(y) > 255)):
                                    #octet out of range
                                    self.IP = ''
                                    return (-4)
                            except:
                                #octet is not a valid integer
                                return (-4)
                    else:
                        #IP Address doesn't have correct amount of octets
                        self.IP = ''
                        return (-4)
                elif (line_list[0].strip() == 'PORT'):
                    self.PORT = line_list[1].strip()
                    #Verify PORT is a number between 0 and 65535
                    try:
                        if ((int(self.PORT) < 0) or (int(self.PORT) > 65535)):
                            #PORT is out of range
                            self.PORT = ''
                            return (-4)
                    except:
                        #PORT is not a valid integer
                        return (-4)
                elif (line_list[0].strip() == 'PROTOCOL'):
                    self.PROTOCOL = line_list[1].strip()
                    if ((self.PROTOCOL != 'UDP') and (self.PROTOCOL != 'TCP')):
                        self.PROTOCOL = ''
                        return (-4)
                elif (line_list[0].strip() == 'SMSD'):
                    self.SMS1 = line_list[1].strip()
                elif (line_list[0].strip() == 'USERNAME'):
                    self.USERNAME = line_list[1].strip()
                elif (line_list[0].strip() == 'PASSWORD'):
                    self.PASSWORD = line_list[1].strip()
                elif (line_list[0].strip() == 'INTERVAL'):
                    self.INTERVAL = line_list[1].strip()
                    #INTERVAL is a number between 0 and 86400 (One Day Maximum)
                    try:
                        if ((int(self.INTERVAL) < 0) or (int(self.INTERVAL) > 65535)):
                            #INTERVAL is out of range
                            self.INTERVAL = ''
                            return (-4)
                    except:
                        #INTERVAL is not a valid integer
                        return (-4)
                else:
                    #Undefined Parameter
                    return (-3)
  
        else:
            #Invalid amount of parameters
            return (-5)
        
        #Function passed
        #Input parameters loaded
        return 0
