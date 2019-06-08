import subprocess
import re

class line_matcher:
    def __init__(self, regexp, handler):
        self.regexp  = re.compile(regexp)
        self.handler = handler


def handle_new_network(line, result, networks):
    # group(1) is the mac address
    networks.append({})
    networks[-1]['Address'] = result.group(1)

def handle_essid(line, result, networks):
    # group(1) is the essid name
    networks[-1]['ESSID'] = result.group(1)

def handle_quality(line, result, networks):
    # group(1) is the quality value
    # group(2) is probably always 100
    networks[-1]['Quality'] = result.group(1) + '/' + result.group(2)
    networks[-1]['Signal level'] = '-' + result.group(3)

def handle_unknown(line, result, networks):
    # group(1) is the key, group(2) is the rest of the line
    networks[-1][result.group(1).strip()] = result.group(2).strip()

class scanner:

    matchers = []
    iface = None
    
    def __init__(self, iface):
        # set interface
        self.iface = iface
        
        # catch the line 'Cell ## - Address: XX:YY:ZZ:AA:BB:CC'
        self.matchers.append(line_matcher(r'\s+Cell \d+ - Address: (\S+)',
                                     handle_new_network))
    
        # catch the line 'ESSID:"network name"
        self.matchers.append(line_matcher(r'\s+ESSID:"([^"]+)"', 
                                     handle_essid))

        # catch the line 'Quality=X/Y  Signal level=X dBm Noise level=Y dBm'
        self.matchers.append(line_matcher(r'\s+Quality=(\d+)/(\d+)\s+Signal level=-(\d+)',
                                     handle_quality))

        # catch any other line that looks like this:
        # Key:value
        self.matchers.append(line_matcher(r'\s+([^:]+):(.+)',
                                     handle_unknown))


    def get_wifi_info(self):
        proc = subprocess.Popen(['/sbin/iwlist', self.iface, 'scan'],
                            stdout=subprocess.PIPE)
        stdout, stderr =  proc.communicate()

        lines = stdout.decode().split('\n')

        networks = []
    
        # read each line of output, testing against the matches above
        # in that order (so that the key:value matcher will be tried last)
        for line in lines:
            for m in self.matchers:
                result = m.regexp.match(line)
                if result:
                    m.handler(line, result, networks)
                    break

        #for n in networks:
            #print 'Found network', n['ESSID'], 'Quality', n['Quality']
            # to see the whole dictionary:
            #print n

        return sorted(networks, key = lambda i: (int(i['Quality'].split('/')[0]), int(i['Signal level'])), reverse=True)

def parse_wifi_info(wifi_info):
    for wifi in wifi_info:
        print('SSID:', wifi['ESSID'])
        print('Address:', wifi['Address'])
        print('Quality:', wifi['Quality'])
        print('Signal level', wifi['Signal level'])
        if 'Authentication Suites (1)' in wifi:
            print('Authentication Suites:', wifi['Authentication Suites (1\
)'].strip())
        print()
    
if __name__ == '__main__':
    s = scanner('wlp3s0')
    result = s.get_wifi_info()
    parse_wifi_info(result)
                                            
