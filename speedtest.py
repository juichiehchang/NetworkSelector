#pip3 install speedtest-cli

import speedtest
import datetime

print(datetime.datetime.now())

servers = []

s = speedtest.Speedtest()
s.get_servers(servers)
s.get_best_server()
s.download()
s.upload()
s.results.share()

res = s.results.dict()

print('ping:', res['ping'])

print('down:', res['download'])

print('uplo:', res['upload'])

print(datetime.datetime.now())
