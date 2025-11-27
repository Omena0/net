from os import chdir
import requests
import socket

# Imports for use in .ui scripts (when using a built executable)
from threading import Thread
import time as t
import Chessnut
import random
import sys

try: chdir('client')
except: ...

API_URL = 'https://omena0.github.io/api'

def apiGet(path,full_path=False):
    """Get a string from api

    Args:
        path (str): api path

    Returns:
        str: string from api
    """
    if not full_path: response = requests.get(f"{API_URL}/{path}")
    else: response = requests.get(f"{path}")
    response.raise_for_status()
    return response.text.strip()

dns_addr = apiGet('net/dns_ip').split(':')
dns_addr = dns_addr[0], int(dns_addr[1])


print(f'DNS Address: {dns_addr}')

localDns = {"localhost":('127.0.0.1',8080)}

def get_from_dns(url:str, nocache=False):
    if not url: return

    url = url.split('/')[0].split('?')[0]
    if url in localDns and not nocache: return localDns[url]

    s = socket.socket()
    s.connect(dns_addr)
    s.send(url.encode())
    addr = s.recv(2048).decode()

    if addr == 'Not found': return None
    if addr == '500 Internal Server Error': return None

    print(addr)

    addr = addr.split(':')
    localDns[url] = addr[0],int(addr[1])

    return addr[0],int(addr[1])

def recvall(s:socket.socket):
    buf = bytes()
    s.settimeout(0.5)
    timeout_count = 0
    while True:
        try: 
            a = s.recv(2048)
            if not a:
                break
            timeout_count = 0
            buf += a
        except socket.timeout:
            timeout_count += 1
            if timeout_count >= 2:
                break

    return buf

def get_file(addr,url):
    s = socket.socket()
    try:
        s.connect(addr)

        print(f'Getting file: {url}')

        s.send(f'/{url}'.encode())
        file = recvall(s)
        s.close()

        return FileNotFoundError if '//404' in file.decode(errors='ignore') else file
    finally:
        try: s.close()
        except: ...

def get_page(url):
    if url.strip() == '': return
    s = socket.socket()
    try:
        s.connect(addr)
    except Exception as e:
        print(e)
        return

    try:
        if '/' not in url: url += '/'
        url = url.split('/',1)[1]

        print(f'Getting file: {url.removesuffix('.ui') if url else 'index'}.ui')

        s.send(f'/{url}'.encode())

        # Page
        return recvall(s).decode()
    finally:
        try: s.close()
        except: ...

def redirect(site:str, unloaded=False):
    import parse

    parse.ui.running = False
    parse.ui.root = None

    parse.scripts = {}
    parse.events  = {}
    parse.objects = {}

    if not unloaded:
        parse.runEvent('onUnload')

    parse.init(redirect,get_page,get_file,get_from_dns,addr,url)

    page = get_page(site)

    if not page: return

    parse.render(page)


# Main loop
while True:
    try:
        import parse

        url = input('URL: ')

        if url.strip() == '': continue
        if url.strip() not in ['localhost','127.0.0.1']:
            addr = get_from_dns(url)
        else:
            addr = '127.0.0.1',8080

        parse.init(redirect,get_page,get_file,get_from_dns,addr,url)

        page = get_page(url)
        if not page: continue

        parse.render(page)

    except Exception as e:
        print(e)
        raise e




