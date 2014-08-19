START /max  C:\Progra~1\Python\Pythonwin\Pythonwin.exe ATC.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max  C:\Progra~1\Python\Pythonwin\Pythonwin.exe GPRS.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max  C:\Progra~1\Python\Pythonwin\Pythonwin.exe NETWORK.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max C:\Progra~1\Python\Pythonwin\Pythonwin.exe MS20.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max C:\Progra~1\Python\Pythonwin\Pythonwin.exe DEBUG_CF.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max C:\Progra~1\Python\Pythonwin\Pythonwin.exe GSM865CF_GPS.py

del *.pyc
del *.pyo