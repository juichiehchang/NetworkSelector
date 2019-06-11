import subprocess

def get_con_info():
    
    proc = subprocess.Popen(['nmcli', 'con', 'show'],
                            stdout=subprocess.PIPE)
    stdout, stderr =  proc.communicate()

    lines = stdout.decode().split('\n')
    
    networks = []
    
    lines = [line for line in lines[1:] if line]
    for line in lines:
        networks += [line.split()[0]]

    return networks

if __name__ == '__main__':
    print(get_con_info())
