import socket
import threading

import settings
from settings import Mode, logging

def get_addr_name(addr):
    ip = addr[0]
    if ip in settings.friendList:
        return settings.friendList[ip]
    else:
        return ip

class ServerThread(threading.Thread):
    def __init__(self, host, port):
        logging.info('Initializing a ServerThread object')
        super().__init__()
        self.__connectedSocks = {}
        #TODO: dict max length may be adjusted later
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__serverSocket.bind((host, port))
        self.__serverSocket.listen(5)
        self.__serverSocket.settimeout(0.3)
        self.__isRunning = False
        logging.info('A ServerThread object created')

    def run(self):
        self.__isRunning = True
        while self.__isRunning:
            try:
                sock, addr = self.__serverSocket.accept()
            except socket.timeout:
                continue
            self.__connectedSocks[addr] = sock
            tSlave = threading.Thread(target=self.server_slave, args=(addr,))
            tSlave.start()
        logging.info('tServer closed')

    def server_slave(self, addr):
        nickname = get_addr_name(addr)
        sock = self.__connectedSocks[addr]
        print('Accept new connection from %s...' % nickname)
        sock.send(b'Welcome')
        emptyStrCounter = 0
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = sock.recv(1024).decode('utf-8')
                logging.info(r'Server got message %r' % message)
                if message == '':
                    emptyStrCounter += 1
                    continue
                else:
                    emptyStrCounter = 0
            except socket.timeout:
                continue
            if message == r'\quit':
                break
            print('%s:> %s' % (nickname, message))
        sock.send(br'\close')
        sock.close()
        print('Connection from %s closed.' % nickname)
        del self.__connectedSocks[addr]

    def close(self):
        logging.info('Set the isRunning flag to False')
        self.__isRunning = False

    def get_connected_socks(self):
        return dict(self.__connectedSocks)

    def say(self, message):
        for sock in self.__connectedSocks.values():
            sock.send(message.encode('utf-8'))

def start_server():
    settings.tServer = ServerThread('', settings.PORT)
    print('Change to SERVER mode...')
    settings.mode = Mode.SERVER
    settings.tServer.start()