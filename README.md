Python
===

Janus Demonstration Python Scripts
These are some demos and random code to use as an example when developing python scripts for the
Janus devices. It's recommended to only utilize the older code as an example, as the older units
will reach EOL as networks remove more 2G support. 

Python1.5.2
--Older code for use in modules like the GSM865CF. 

-Pythonwin IDE
--The 1.5.2+ IDE installer

-GSM865CF Plug-In Terminus GPS Demo
--This demonstration takes advantage of the evaluation kit's null modem function.
 It takes GPS data and forwards it to a listening server via a socket dial. 

-Terminus_Serial_to_GPRS_Demo_v2
--This demonstration creates a bridge via socket dial to a listening server.
 It takes data from the local serial port and sends it, while receiving and printing incoming data.

-TrackerDemo
--This is the demo python code for a tracker unit developed by Janus. Please note that there is much of this
 that is out of context, such as some of the I/O handling which is unusable without the accompanying components
 of the design. However, it has much covered that can be ported to your application with a little tooling.


Python2.7.2
--Newer code for use in modules such as the HSPA910CF.

-SMS Response Demo
--This demo is a simple SMS echo. The user guide is more generalized for the Terminus T2 Janus device
 but the instructions that cover the demo are still relevant and useful on their own. 

-Python272LibPC_Emulation
--This is the library of normally embedded modules that can be helpful for locally running the code or debugging.



 



