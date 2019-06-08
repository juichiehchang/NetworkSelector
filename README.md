# WifiSelector
Wifi selector for linux system implemetend with NetworkManager
## Usage
1. Run "python3 set_pw.py" which will prompt you to enter all the (ssid, identity, password) pairs you know
2. Run "sudo python3 traverse_wifi.py" which will try to connect to the wifis scanned by "iwlist" one at a time