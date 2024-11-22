from threading import Thread
import socket
import json

s = socket.socket()

addr = ('127.0.0.1',53)

s.bind(addr)

sites = json.load(open('data/sites.json'))

def csHandler(cs:socket.socket,addr:tuple[str,int]):
    global sites
    while True:
        try:
            msg = cs.recv(1024).decode()
            if msg.strip() == '': return

            site = sites.get(msg,'Not found')
            cs.send(site.encode())
            print(f'Served site: {msg} -> {site}')

        except ConnectionAbortedError:
            print(f'[-] {addr}')
            return

        except Exception as e:
            print(f'[-] {addr} [{e}]')
            try: cs.send('500 Internal Server Error'.encode())
            except: ...
            return

s.listen(5)

print(f'Running DNS on {addr}')

while True:
    cs,addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler,args=[cs,addr],daemon=True).start()

