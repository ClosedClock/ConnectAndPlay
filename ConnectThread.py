import socket
import threading
from queue import Queue

import settings
from settings import Mode, logging

class ConnectThread(threading.Thread):
    def __init__(self, addr, sock):
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
        emptyStrCounter = 0
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = sock.recv(1024).decode('utf-8')
                logging.info(r'Got message "%s"' % message)
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
        settings.mode = Mode.NORMAL
        print('Connection to %s closed.' % nickname)

    def deal_message(self, message):
        if message[0] == '\\':
            logging.info('This is a command from: %s' % self.get_nickname())
            self.__queue.put(message)
        else:
            #print(command)
            print('%s:> %s' % (self.get_nickname(), message))

    def get_message(self, timeout=None):
        return self.__queue.get(True, timeout)


    def send_message(self, message):
        self.__sock.send(message.encode('utf-8'))


    def quit(self):
        logging.info('Set the ClientThread isRunning flag to False')
        self.__isRunning = False


    def get_connected_server(self):
        return self.__addr


