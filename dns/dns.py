import socket
from threading import Thread
import json
import time as t

s = socket.socket()

addr = ('127.0.0.1',53)

s.bind(addr)

sites = json.load(open('data/sites.json'))

ratelimit = {}

def csHandler(cs:socket.socket,addr:tuple[str,int]):
    while True:
        try:
            msg = cs.recv(1024).decode()
            print(msg)
            rl = ratelimit.get(cs,None)
            if rl and rl < t.time():
                cs.send('429 Too Many Requests'.encode())
                continue

            cs.send(sites.get(msg,'Not found').encode())
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

