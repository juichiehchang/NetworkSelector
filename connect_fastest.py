import os
import subprocess
import time
from get_pw import get_pw_dicts
from get_con import get_con_info
from scan import scanner, parse_wifi_info
import speedtest

class traverse:

    wifi_list = None
    psk_dict = None
    eap_dict = None
    s = None
    iface = None
    con = None
    
    def __init__(self, iface):
        os.system('sudo rm -f /etc/NetworkManager/system-connections/* >/dev/null 2>&1')
        os.system('sudo systemctl restart NetworkManager >/dev/null >/dev/null 2>&1')
        time.sleep(0.01)
        self.iface = iface
        
        # get wifi information with iwlist
        self.s = scanner(self.iface)
        self.wifi_list = self.s.get_wifi_info()

        # parse all detected wifi
        parse_wifi_info(self.wifi_list)
        
        # get already-known connections
        self.con = get_con_info()

        self.speedLists = []
        
    def get_passwd(self):
        # get the identities and passwords for wifi connections
        [self.psk_dict, self.eap_dict] = get_pw_dicts()

        #print(self.psk_dict)
        #print(self.eap_dict)

        # add psk config into network-manager
        for name in self.psk_dict:
            #print('name: {}'.format(name))
            if name not in self.con:
                #print('Adding "{}"'.format(name))
                os.system('nmcli con add type wifi con-name {} ifname {} ssid {} >/dev/null 2>&1'.format(name, self.iface, name))
            #print('Setting "{}" with password "{}" in system-connections'.format(name, self.psk_dict[name]))
            os.system('nmcli con modify {} wifi-sec.key-mgmt wpa-psk wifi-sec.psk {} >/dev/null 2>&1'.format(name, self.psk_dict[name]))
                
        # add eap config into network-manager
        for name in self.eap_dict:
            #print('name: {}'.format(name))
            # wifi hasn't been added to con
            if name not in self.con:
                self.eap_add_con(name, self.eap_dict[name][0])
                time.sleep(2)
            # check if password has been added to network-manager, if not,  add it 
            self.eap_add_pw(name, self.eap_dict[name][1])
            
        #for wifi in self.wifi_list:
        #    name = wifi['ESSID']
        #    if 'Authentication Suites (1)' in wifi:
        #        if wifi['Authentication Suites (1)'] == 'EAP' and name in self.eap_dict:
        #            print('name: {}'.format(name))
        #            # wifi hasn't been added to con
        #            if name not in self.con:
        #                self.add_con(name, self.eap_dict[name][0])
        #            # check if password has been added to network-manager, if not,  add it 
        #            self.add_pw(name, self.eap_dict[name][1])

        # restart network-manager
        print('\nRestarting NetworkManager\n')
        os.system("systemctl restart NetworkManager >/dev/null 2>&1")
        time.sleep(2)

    def eap_add_con(self, name, identity):
        #print('Adding "{}" with identity: "{}" to con'.format(name, identity))
        os.system('nmcli connection add type wifi con-name "{}" ifname {} ssid "{}" -- wifi-sec.key-mgmt wpa-eap 802-1x.eap peap 802-1x.phase2-auth mschapv2 802-1x.identity "{}" >/dev/null 2>&1'.format(name, self.iface, name, identity))

    def eap_add_pw(self, name, password):
        lines = None
        with open('/etc/NetworkManager/system-connections/' + name, 'r') as f:
            contents = f.read()
            # check if password already exists
            if 'password=' not in contents:
                #print('Adding "{}" with password "{}" to system-connections'.format(name, password))
                f.seek(0)
                lines = f.readlines()
                #print(lines)
                for i, line in enumerate(lines):
                    if line.startswith('[802-1x]'):
                        # write password into file
                        #print(lines[i])
                        lines[i] = lines[i] + 'password=' + password + '\n'
                        break
                    
        with open('/etc/NetworkManager/system-connections/' + name, 'w') as f:
            for line in lines:
                f.write(line)

    def testSpeed(self, name):
        print('Testing ' + name)
        servers = []
        s = speedtest.Speedtest()
        s.get_servers(servers)
        s.get_best_server()
        s.download()
        s.results.share()
        res = s.results.dict()
        self.speedLists.append((name, res['download']))

    def connect(self, wifi):

        name = wifi['ESSID']
        #print('name: {}'.format(name))
        
        # check authentication suites
        if 'Authentication Suites (1)' in wifi:
            authentication = wifi['Authentication Suites (1)']
            if authentication == 'EAP' or '802.1x':
                # eap requires identity and password
                if name in self.eap_dict:
                    [identity, password] = self.eap_dict[name]
                    # try to connect
                    try:
                        result = self.connection(name)
                    except Exception as e:
                        pass#print("Couldn't connect to name : {}. {}".format(name, e))
                    else:
                        if result:
                            self.testSpeed(name)
                """else:
                    print('Does not have the identity and password for "{}"'.format(name))"""
            elif authentication == 'PSK':
                # psk requires only password
                if name in self.psk_dict:
                    password = self.psk_dict[name]
                    #print('Connecting to "{}" with password "{}"'.format(name, password))
                    # try to connect
                    try:
                        result = self.connection(name)
                    except Exception as e:
                        print("GG")
                        pass#print("Couldn't connect to name : {}. {}".format(name, e))
                    else:
                        if result:
                            self.testSpeed(name)
                """else:
                    print('Does not have the password for "{}"'.format(name))"""
                    
    def connection(self, name):
        try:
            os.system("nmcli con up {} >/dev/null 2>&1".format(name))
        except:
            raise
        else:
            return True

    def try_all(self):
        #for wifi in self.wifi_list:
        #    if wifi['ESSID'] == 'iPhone':
        #        self.connect(wifi)
        
        for wifi in self.wifi_list:
            self.connect(wifi)
            
if __name__ == '__main__':
    t = traverse('wlp3s0')
    t.get_passwd()
    t.try_all()
    t.speedLists.sort(key=lambda sp: sp[1], reverse=True)
    print(t.speedLists)
