import socket

dns_addr = ('0.tcp.eu.ngrok.io',15870)

localDns = {}

def get_from_dns(url:str, nocache=False):
    url = url.split('/')[0].split('?')[0]
    print(localDns)
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
    s = socket.socket()
    addr = get_from_dns(url)
    print(addr)
    s.connect(addr)
    if '/' not in url: url += '/'
    print(url)
    s.send(('/'+url.split('/')[1]+'.ui').encode())
    page = s.recv(2048).decode()
    return page


while True:
    import parse
    parse.render(get_page(input('URL: ')))




