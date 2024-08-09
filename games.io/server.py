from threading import Thread
import time as t
import socket
import os

s = socket.socket()

addr = ('127.0.0.1',8080)

s.bind(addr)

disclaimer = '\n\nTHIS IS A WEBSITE FOR THE NET PROJECT: https://github.com/Omena0/net'

# Support online games
games:dict[id:list[socket.socket]] = {}
names:dict[socket.socket:str] = {}


def csHandler(cs:socket.socket,addr:tuple[str,int]):
    while True:
        try:
            msg = cs.recv(2048).decode()
            if msg.strip() == '': return

            # Support online games
            if msg.startswith('!'):
                msg = msg.removeprefix('!').split('|')
                print(msg)

                if msg[0] == 'create_game':
                    id = msg[1]
                    games[id] = [cs]

                elif msg[0] == 'join_game':
                    id = msg[1]
                    if id not in games.keys():
                        t.sleep(0.05)
                        cs.send(b'E|Game not found.')
                        del id
                        continue

                    games[id].append(cs)
                    t.sleep(0.05)
                    cs.send('|'.join([names[cs] for cs in games[id]]).encode())

                    for i in games[id]:
                        if i == cs: continue
                        i.send(f'JOIN|{names[cs]}'.encode())
                
                elif msg[0] == 'set_name':
                    name = msg[1]
                    names[cs] = name
                
                elif msg[0] == 'broadcast':
                    for i in games[id]:
                        if i == cs: continue
                        i.send('|'.join(msg).encode())
                    
                elif msg[0] == 'quit':
                    for i in games[id]:
                        i.send(f'LEFT|{names[cs]}'.encode())
                    games[id].remove(cs)
                    names.pop(cs)
                    try: cs.close()
                    except: ...

                continue

            msg = msg.removeprefix('/')
            if msg == '': msg = 'index.ui'
            if '.' not in msg: msg += '.ui'
            
            msg = msg.replace('..','').replace(':','')

            path = msg.split('/')
            cpath = '.'
            for i in path:
                if i.count('.') == 0:
                    if i in os.listdir(cpath):
                        cpath = f'{cpath}/{i}'
                    else:
                        with open('404.ui','rb') as f: site = f.read()
                    continue

                elif i.split('.')[1] not in ['ui','png','jpeg','txt']:
                    cs.send(f'400 Bad Request{disclaimer}'.encode())
                    print('400 Bad Request')
                    continue

                if i not in os.listdir(cpath):
                    with open('404.ui','rb') as f: site = f.read()

                else:
                    with open(f'{cpath}/{i}','rb') as f: site = f.read()
            
            print(f'Serving file: {msg}')
            cs.send(site)

        except ConnectionAbortedError:
            print(f'[-] {addr}')
            return
        
        except Exception as e:
            print(f'[-] {addr} [{e}]')
            try: cs.send(f'500 Internal Server Error'.encode())
            except: ...
            return

s.listen(5)

print(f'Running server on {addr}')

while True:
    cs,addr = s.accept()
    print(f'[+] {addr}')
    Thread(target=csHandler,args=[cs,addr],daemon=True).start()

