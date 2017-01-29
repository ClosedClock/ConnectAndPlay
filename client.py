import socket
import threading

import settings
from settings import Mode, logging

class ClientThread(threading.Thread):
    def __init__(self, host, port):
        logging.info('Initializing a ServerThread object')
        super().__init__()
        self.__serverAddr = (host, port)
        self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clientSocket.settimeout(0.3)
        self.__isRunning = False
        logging.info('A ServerThread object created')

    def get_nickname(self):
        return settings.get_addr_name(self.__serverAddr)

    def run(self):
        self.__isRunning = True
        sock = self.__clientSocket
        sock.connect(self.__serverAddr)
        nickname = self.get_nickname()
        print('Connected to %s' % nickname)
        emptyStrCounter = 0
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = sock.recv(1024).decode('utf-8')
                logging.info(r'Client got message "%s"' % message)
                if message == '':
                    emptyStrCounter += 1
                    continue
                else:
                    emptyStrCounter = 0
            except socket.timeout:
                continue
            if message == r'\close':
                break
            print('%s>: %s' % (nickname, message))
        sock.send(br'\quit')
        sock.close()
        settings.mode = Mode.NORMAL
        print('Connection to %s closed.' % nickname)

    def quit(self):
        self.__clientSocket.send(br'\quit')
        self.__isRunning = False

    def say(self, message):
        self.__clientSocket.send(message.encode('utf-8'))

    def get_connected_server(self):
        return self.__serverAddr


def connect_to(str):
    if str in settings.friendList.values():
        for ip, nickname in settings.friendList.items():
            if nickname == str:
                correspondIp = ip
                break
    else:
        correspondIp = str
    settings.tClient = ClientThread(correspondIp, settings.PORT)
    print('Change to CLIENT mode...')
    settings.mode = Mode.CLIENT
    settings.tClient.start()