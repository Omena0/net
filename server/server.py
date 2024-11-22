import socket
from threading import Thread
import os
import time as t

s = socket.socket()

addr = ('127.0.0.1',8080)

s.bind(addr)

disc = '\n\nTHIS IS A WEBSITE FOR THE NET PROJECT: https://github.com/Omena0/net'

def csHandler(cs:socket.socket,addr:tuple[str,int]):
    while True:
        try:
            msg = cs.recv(1024)
            if msg.decode().strip() == '': return
            msg = msg.decode().removeprefix('/')
            if msg == '': msg = 'index.ui'
            if '.' not in msg: msg += '.ui'

            msg = msg.replace('..','').replace(':','')

            path = msg.split('/')
            searchPath = '.'

            for i in path:
                if i.count('.') == 0:
                    if i in os.listdir(searchPath):
                        searchPath = f'{searchPath}/{i}'
                    else:
                        with open('404.ui','rb') as f: site = f.read()
                    continue

                elif i.split('.')[1] not in ['ui','png','jpeg','txt']:
                    cs.send(f'400 Bad Request{disc}'.encode())
                    print('400 Bad Request')
                    continue

                if i not in os.listdir(searchPath):
                    with open('404.ui','rb') as f: site = f.read()

                else:
                    with open(f'{searchPath}/{i}','rb') as f: site = f.read()

            print(f'Serving file: {msg}')
            cs.send(site)

        except ConnectionAbortedError:
            print(f'[-] {addr}')
            return

        except Exception as e:
            print(f'[-] {addr} [{e}]')
            try: cs.send(f'500 Internal Server Error{disc}'.encode())
            except: ...
            return

s.listen(5)

print(f'Running server on {addr}')

while True:
    cs,addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler,args=[cs,addr],daemon=True).start()

