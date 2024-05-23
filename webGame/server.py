import socket
from threading import Thread
import os
import time as t

s = socket.socket()

addr = ('127.0.0.1',8080)

s.bind(addr)

ratelimit = {}

def csHandler(cs:socket.socket,addr:tuple[str,int]):
    while True:
        try:
            msg = cs.recv(1024).decode().removesuffix('.ui').removeprefix('/')
            if msg == '': msg = 'index'
            print(f'Serving site: {msg}')
            rl = ratelimit.get(cs,None)
            if rl and rl < t.time():
                cs.send('429 Too Many Requests'.encode())
                print('429 Too Many Requests')
                continue
            
            if not msg.endswith('.ui'): msg += '.ui'
            
            if msg not in os.listdir('.'):
                with open('404.ui') as f: site = f.read()
            
            else:
                with open(msg) as f: site = f.read()
            
            cs.send(site.encode())
            ratelimit[cs] = t.time()

        except ConnectionAbortedError:
            print(f'[-] {addr}')
            return
        
        except Exception as e:
            print(f'[-] {addr} [{e}]')
            try: cs.send('500 Internal Server Error\n\nTHIS IS NOT A REGULAR WEBSITE, DONT USE IT AS ONE!\nTHIS IS A WEBSITE FOR THE NET PROJECT: https://gthub.com/Omena0/net'.encode())
            except: ...
            return

s.listen(5)

print(f'Running server on {addr}')

while True:
    cs,addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler,args=[cs,addr]).start()

