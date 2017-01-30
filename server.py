import socket
import threading
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
        sock = self.__sock
        nickname = self.get_nickname()
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
            self.deal_message(message)
        sock.send(br'\quit')
        sock.close()
        print('Connection from %s closed.' % nickname)

    def deal_message(self, message):
        if message[0] == '\\':
            logging.info('This is a command from: %s' % self.get_nickname())
            if settings.gameOpponent != '':
                self.__queue.put(message)
            else:
                if message == r'\janken':
                    print('Received a game request %s from %s' % (message, self.get_nickname()))
                    settings.gameOpponent = self.__addr
                else:
                    print('Received strange command: %s' % message)

        else:
            #print(command)
            print('%s:> %s' % (self.get_nickname(), message))

    def get_message(self, timeout=None):
        return self.__queue.get(True, timeout)

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

    def get_clients_addr(self):
        return self.__clientsDict.keys()

    def get_slave_thread(self, addr=''):
        if len(self.__clientsDict) == 0:
            raise KeyError('No connection')

        if addr == '':
            if len(self.__clientsDict) == 1:
                return self.__clientsDict.values()[0]
            else:
                raise KeyError('Address needed')
        else:
            try:
                return self.__clientsDict[addr]
            except KeyError:
                raise KeyError('Address not in clientDict when get_slave_thread')

    # def get_message(self, addr):
    #     try:
    #         self.__clientsDict[addr].get_message()
    #     except KeyError as e:
    #         raise KeyError('Address not in clientDict when get_message')

    # def send_message(self, addr, message):
    #     try:
    #         self.__clientsDict[addr].send_message(message)
    #     except KeyError as e:
    #         raise KeyError('Address not in clientDict when get_message')

    def say(self, message):
        for addr in self.__clientsDict:
            self.__clientsDict[addr].send_message(message)

    # def get_clients_num(self):
    #     return len(self.__clientsDict)