from tkinter import messagebox
import requests
import socket
import os

# Imports for use in .ui scripts
import threading
import random
import time
import sys

try: os.chdir('client')
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

localDns = {}

def get_from_dns(url:str, nocache=False):
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

    s.send(f'/{url}'.encode())
    page = s.recv(4294967296)

    return page

def get_page(url):
    if url.strip() == '': return
    s = socket.socket()
    try: s.connect(addr)
    except: return
    
    if '/' not in url: url += '/'
    url = url.split('/',1)[1]

    s.send(f'/{url}'.encode())
    page = s.recv(4294967296).decode()

    return page



def redirect(site:str):
    import parse
    parse.init(redirect,get_page,get_file,get_from_dns,addr)
    page = get_page(site)
    if not page: return
    parse.render(page)


while True:
    import parse
    
    url = input('URL: ')
    if url.strip() == '': continue
    addr = get_from_dns(url)
    
    parse.init(redirect,get_page,get_file,get_from_dns,addr)
    
    page = get_page(url)
    if not page: continue
    try: parse.render(page)
    except Exception as e:
        print(e.with_traceback(None))
        raise e




