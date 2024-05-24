import socket
from threading import Thread
import os
import time as t

s = socket.socket()

addr = ('127.0.0.1',8080)

s.bind(addr)

def csHandler(cs:socket.socket,addr:tuple[str,int]):
    while True:
        try:
            msg = cs.recv(1024).decode().removeprefix('/')
            if msg == '': msg = 'index.ui'
            if '.' not in msg: msg += '.ui'
            
            msg = msg.replace('..','').replace(':','')
            
            if msg.split('.')[1] not in ['ui','png','jpeg','txt']:
                cs.send('400 Bad Request'.encode())
                print('400 Bad Request')
                continue

            print(f'Serving file: {msg}')
            
            if msg not in os.listdir('.'):
                with open('404.ui','rb') as f: site = f.read()
            
            else:
                with open(msg,'rb') as f: site = f.read()
            
            cs.send(site)

        except ConnectionAbortedError:
            print(f'[-] {addr}')
            return
        
        except Exception as e:
            print(f'[-] {addr} [{e}]')
            msg = '\n\nTHIS IS NOT A REGULAR WEBSITE, DONT USE IT AS ONE!\nTHIS IS A WEBSITE FOR THE NET PROJECT: https://gthub.com/Omena0/net' if 'GET' in msg else ''
            try: cs.send(f'500 Internal Server Error{msg}'.encode())
            except: ...
            return

s.listen(5)

print(f'Running server on {addr}')

while True:
    cs,addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler,args=[cs,addr]).start()

