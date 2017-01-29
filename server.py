import socket
import threading
import re
from queue import Queue

import settings
from settings import Mode, logging



class ServerSlaveThread(threading.Thread):
    def __init__(self, sock, addr):
        logging.info('Initializing a ServerSlaveThread object')
        super().__init__()
        self.__queue = Queue()
        self.__addr = addr
        self.__sock = sock
        self.__isRunning = False

    def get_nickname(self):
        return settings.get_addr_name(self.__addr)

    def run(self):
        self.__isRunning = True
        nickname = self.get_nickname()
        print('Accept new connection from %s...' % nickname)
        self.__sock.send(b'Welcome')
        emptyStrCounter = 0
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = self.__sock.recv(1024).decode('utf-8')
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
            self.deal_message(message)
        self.__sock.send(br'\close')
        self.__sock.close()
        print('Connection from %s closed.' % nickname)

    def deal_message(self, message):
        if message[0] == '\\':
            logging.info('This is a command from: %s' % self.get_nickname())
            self.__queue.put(message)
        else:
            #print(command)
            print('%s:> %s' % (self.get_nickname(), message))

    def get_message(self):
        return self.__queue.get()
        #TODO use get(True)?

    def send_message(self, message):
        self.__sock.send(message.encode('utf-8'))

    def close(self):
        logging.info('Set the ServerSlaveThread isRunning flag to False')
        self.__isRunning = False


class ServerThread(threading.Thread):
    def __init__(self, host, port):
        logging.info('Initializing a ServerThread object')
        super().__init__()
        self.__clientsDict = {}
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
            tSlave = ServerSlaveThread(sock, addr)
            self.__clientsDict[addr] = tSlave
            tSlave.start()
        logging.info('tServer closed')

    def close(self):
        logging.info('Set the ServerThread isRunning flag to False')
        self.__isRunning = False
        for addr in self.__clientsDict:
            self.__clientsDict[addr].close()
        self.__clientsDict = {}

    def get_clients(self):
        return self.__clientsDict.keys()

    def say(self, message):
        for addr in self.__clientsDict:
            self.__clientsDict[addr].send_message(message)

def start_server():
    settings.tServer = ServerThread('', settings.PORT)
    print('Change to SERVER mode...')
    settings.mode = Mode.SERVER
    settings.tServer.start()