import json

class pw:
    
    def __init__(self):
        self.data = {}
        self.data['psk'] = []
        self.data['eap'] = []
        
    def add_psk(self, ssid, password):
        self.data['psk'].append({'ssid': ssid, 'password': password})
    
    def add_eap(self, ssid, identity, password):
        self.data['eap'].append({'ssid': ssid, 'identity': identity, 'password': password})

    def dump(self):
        with open('password.json', 'w') as outfile:
            json.dump(self.data, outfile)
    
if __name__ == '__main__':
    print('\nThis program wil help you generate "password.json" which contains all known identities and passwords for wifi connections')

    p = pw()

    while True:
        print('"SSID":')
        ssid = input('> ').strip()
        if ssid == "":
            break

        print('"identity" for "{}", press "Enter" if not needed'.format(ssid))
        identity = input('> ').strip()
        
        print('"password" for "{}"'.format(ssid))
        password = input('> ').strip()

        print('')

        if identity == "":
            p.add_psk(ssid, password)
        else:
            p.add_eap(ssid, identity, password)

    p.dump()
