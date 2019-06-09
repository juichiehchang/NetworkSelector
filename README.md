# WifiSelector
Wifi selector for linux system implemetend with NetworkManager
## Usage
1. Run "python3 set_pw.py" which will prompt you to enter all the (ssid, identity, password) pairs you know
2. Run "sudo python3 traverse_wifi.py" which will try to connect to the wifis scanned by "iwlist" one at a time

## GUI.py 
1. include this as a library, and create (Application) object to open GUI
2. Remember to modify the wifi list at line 30
3. Output speed test result to PageTwo and replace line 101
4. Call Application.show_frame in main process to switch from PageOne to PageTwo

Modified Date: 2019/6/9 11:01
