import json

def get_pw_dicts():
    psk_dict = {}
    eap_dict = {}
    with open('password.json') as jsonfile:
        data = json.load(jsonfile)
        for psk in data['psk']:
            psk_dict[psk['ssid']] = psk['password']
            print(psk['ssid'], psk['password'])
        for eap in data['eap']:
            eap_dict[eap['ssid']] = [eap['identity'], eap['password']]

    return [psk_dict, eap_dict]

if __name__ == '__main__':
    [psk_dict, eap_dict] = get_pw_dicts()
    print(psk_dict)
    print(eap_dict)
            
