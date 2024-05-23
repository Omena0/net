import socket

dns_addr = "2.tcp.eu.ngrok.io", 16379

localDns = {}

def get_from_dns(url:str, nocache=False):
    url = url.split('/')[0].split('?')[0]
    if url in localDns and not nocache: return localDns[url]
    s = socket.socket()
    s.connect(dns_addr)
    s.send(url.encode())
    addr = s.recv(128).decode()
    if addr == 'Not found': return None
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


while True:
    import parse
    page = get_page(input('URL: '))
    if not page: continue
    try: parse.render(page)
    except Exception as e:
        print(e.with_traceback(None))




