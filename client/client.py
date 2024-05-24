import socket
import json
import os

# Imports for use in .ui scripts
import threading
import keyboard
import random
import time
import sys


try: os.chdir('client')
except: ...

config = json.load(open('config.json'))

dns_addr = tuple(config['dns_addr'])

localDns = {}

def get_from_dns(url:str, nocache=False):
    url = url.split('/')[0].split('?')[0]
    if url in localDns and not nocache: return localDns[url]
    s = socket.socket()
    s.connect(dns_addr)
    s.send(url.encode())
    addr = s.recv(128).decode()
    if addr == 'Not found': return None
    print(addr)
    addr = addr.split(':')
    localDns[url] = addr[0],int(addr[1])
    return addr[0],int(addr[1])

def get_page(url):
    if url.strip() == '': return
    s = socket.socket()
    addr = get_from_dns(url)
    try: s.connect(addr)
    except: return
    if '/' not in url: url += '/'
    s.send(('/'+url.split('/')[1]+'.ui').encode())
    page = s.recv(4098).decode()
    return page

def redirect(site:str):
    import parse
    parse.init(redirect)
    page = get_page(site)
    if not page: return
    try: parse.render(page)
    except: return


while True:
    import parse
    parse.init(redirect)
    
    page = get_page(input('URL: '))
    if not page: continue
    try: parse.render(page)
    except Exception as e:
        print(e.with_traceback(None))
        raise e




