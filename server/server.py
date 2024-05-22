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
            msg = cs.recv(1024).decode().removesuffix('.ui')
            print(msg)
            rl = ratelimit.get(cs,None)
            if rl and rl < t.time():
                cs.send('429 Too Many Requests'.encode())
                continue
            
            if not msg.endswith('.ui'): msg += '.ui'
            if msg not in os.listdir('.'):
                with open('404.ui') as f: cs.send(f.read().encode())
                continue
            
            with open(msg) as f: site = f.read()
            
            cs.send(site.encode())
            ratelimit[cs] = t.time()

        except Exception as e:
            print(e)
            try: cs.send('500 Internal Server Error'.encode())
            except: ...
            return

s.listen(5)

while True:
    cs,addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler,args=[cs,addr]).start()

