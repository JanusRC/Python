START /max  C:\Progra~1\Python\Pythonwin\Pythonwin.exe ATC.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max  C:\Progra~1\Python\Pythonwin\Pythonwin.exe GPRS.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max C:\Progra~1\Python\Pythonwin\Pythonwin.exe JANUS_SER.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max C:\Progra~1\Python\Pythonwin\Pythonwin.exe NETWORK.py

PING 1.1.1.1 -n 2 -w 1 >NUL

START /max C:\Progra~1\Python\Pythonwin\Pythonwin.exe TerminusS2G.py

del *.pyc