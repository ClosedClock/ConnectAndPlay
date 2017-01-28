import socket

from settings import *

def connectTo(addr):
    global connectedServer
    global mode
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((addr, 8887))
    mode = Mode.CLIENT
    connectedServer = s
    print(s.recv(1024).decode('utf-8'))