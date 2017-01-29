import socket
import threading

import settings
from settings import Mode, logging

def get_sock_name(addr):
    #TODO: serch a list and get the nickname for addr
    return addr

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
            sockName = get_sock_name(addr)
            self.__connectedSocks[sockName] = sock
            tSlave = threading.Thread(target=self.server_slave, args=(sockName, addr))
            tSlave.start()
        logging.info('tServer closed')

    def server_slave(self, sockName, addr):
        sock = self.__connectedSocks[sockName]
        print('Accept new connection from %s:%s...' % addr)
        sock.send(b'Welcome!')
        while self.__isRunning:
            try:
                message = sock.recv(1024)
                logging.info(r'Server got message %s' % message)
            except socket.timeout:
                continue
            print('%s:> %s' % (addr, message.decode('utf-8')))
            if message.decode('utf-8') == r'\quit':
                break
        sock.send(r'\close'.encode('utf-8'))
        sock.close()
        print('Connection from %s:%s closed.' % addr)
        del self.__connectedSocks[sockName]

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