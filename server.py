import socket
import threading

import settings
from settings import Mode

def waiting(s):
    sock, addr = s.accept()
    settings.connectedSocks.append(sock)
    print('Accept new connection from %s:%s...' % addr)
    sock.send(b'Welcome!')
    while True:
        message = sock.recv(1024)
        print('%s:> %s' % (addr + message.decode('utf-8')))
        if message.decode('utf-8') == '\\exit' or mode == 'NORMAL':
            break
    sock.close()
    print('Connection from %s:%s closed.' % addr)


def startServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8887))
    s.listen(5)
    settings.mode = Mode.SERVER
    print('Change to connecting mode...')
    pWaiting = threading.Thread(target=waiting, args=(s,))
    pWaiting.start()