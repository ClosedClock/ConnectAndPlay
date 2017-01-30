import socket
import threading

import settings
from settings import Mode, logging
from connect_thread import ConnectThread


class ServerSlaveThread(ConnectThread):
    def __init__(self, sock, addr):
        logging.info('Initializing a ServerSlaveThread object')
        super().__init__(sock, addr)
        logging.info('A ServerSlaveThread object created')

    def run(self):
        self.send_message('Welcome')
        print('Accept new connection from %s...' % self.get_nickname())
        super().run()
        print('Connection from %s closed.' % self.get_nickname())

    def quit(self):
        logging.info('Set the ServerSlaveThread isRunning flag to False')
        super().quit()


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
            self.__clientsDict[addr].quit()
        self.__clientsDict = {}

    def get_clients_addr(self):
        return self.__clientsDict.keys()

    def get_slave_thread(self, ip=None):
        if len(self.__clientsDict) == 0:
            raise KeyError('No connection')

        if ip == None:
            if len(self.__clientsDict) == 1:
                for k in self.__clientsDict:
                    return self.__clientsDict[k]
            else:
                raise KeyError('Address needed')
        else:
            for addr in self.__clientsDict:
                if addr[0] == ip:
                    return self.__clientsDict[addr]
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