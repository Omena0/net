from tkinter import messagebox
import requests
import socket
from os import chdir

# Imports for use in .ui scripts
import threading
import random
import time
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
    if url == '': return
    url = url.split('/')[0].split('?')[0]
    if url in localDns and not nocache: return localDns[url]
    s = socket.socket()
    s.connect(dns_addr)
    s.send(url.encode())
    addr = s.recv(128).decode()
    if addr == 'Not found': return None
    if addr == '500 Internal Server Error': return None
    print(addr)
    addr = addr.split(':')
    localDns[url] = addr[0],int(addr[1])
    return addr[0],int(addr[1])

def get_file(addr,url):
    s = socket.socket()
    s.connect(addr)

    print(f'Getting file: {url}')
    
    s.send(f'/{url}'.encode())
    page = s.recv(4294967296)

    return page

def get_page(url):
    if url.strip() == '': return
    s = socket.socket()
    try: s.connect(addr)
    except Exception as e:
        print(e)
        return
    
    if '/' not in url: url += '/'
    url = url.split('/',1)[1]
    
    print(f'Getting file: {url.removesuffix('.ui') if url else 'index'}.ui')
    
    s.send(f'/{url}'.encode())
    page = s.recv(4294967296).decode()

    return page

def redirect(site:str):
    import parse
    parse.init(redirect,get_page,get_file,get_from_dns,addr,url)
    page = get_page(site)
    if not page: return
    parse.render(page)


while True:
    try:
        import parse

        #url = input('URL: ')
        url = 'localhost/g/chess'
        if url.strip() == '': continue
        if url.strip() not in ['localhost','127.0.0.1']:
            addr = get_from_dns(url)
        else:
            addr = '127.0.0.1',8080

        parse.init(redirect,get_page,get_file,get_from_dns,addr,url)

        page = get_page(url)
        if not page: continue

        parse.render(page)
        exit()

    except Exception as e:
        print(e)
        raise e




