import socket
import threading
import logging
import tkinter as tk
from queue import Queue
import settings

from connect_GUI import ConnectGUI

class ServerSlaveThread(threading.Thread):
    def __init__(self, sock):
        logging.info('Initializing a ServerSlaveThread object')
        super().__init__()
        self.__sock = sock
        self.__queue = Queue()
        self.__isRunning = True
        logging.info('A ServerSlaveThread object created')

    def run(self):
        emptyStrCounter = 0
        sock = self.__sock
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = sock.recv(1024).decode('utf-8')
                logging.info(r'Got message "%s"' % message)
                if message == '':
                    emptyStrCounter += 1
                    continue
                else:
                    emptyStrCounter = 0
                logging.info('Putting message %s into the queue' % message)
            except socket.timeout:
                continue
            self.__queue.put(message)
        sock.close()

    def get_message(self):
        return self.__queue.get(False)

    def has_message(self):
        return not self.__queue.empty()

    def send_message(self, message):
        self.__sock.send(message.encode('utf-8'))

    def quit(self):
        logging.info('Set the ServerSlaveThread isRunning flag to False')
        # self.__sock.send(r'\quit'.encode('utf-8'))
        self.__isRunning = False



class ServerGUI(ConnectGUI):
    def __init__(self, host, port):
        logging.info('Initializing a ServerGUI object')
        super().__init__()

        self.__clientsDict = {}
        #TODO: dict max length may be adjusted later
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.settimeout(0.3)
        self.__sock.bind((host, port))
        self.__sock.listen(5)

        self.__serverThread = threading.Thread(target=self.waiting)
        self.__serverThread.start()
        logging.info('A ServerGUI object created')

    def waiting(self):
        while self.isRunning():
            try:
                sock, addr = self.__sock.accept()
            except socket.timeout:
                continue
            tSlave = ServerSlaveThread(sock)
            self.__clientsDict[addr] = tSlave
            tSlave.start()
            print('Accept new connection from %s...' % settings.get_addr_name(addr))
        logging.info('tServer closed')
        self.__sock.close()


    def check_message(self):
        for addr, clientThread in self.__clientsDict.items():
            while clientThread.has_message():
                message = clientThread.get_message()
                logging.info('Got message from %s: %s' % (addr, message))
                self.deal_message(addr, message)
        self.after(100, self.check_message)

    def deal_message(self, addr, message):
        if message[0] == '\\':
            logging.info('This is a command from: %s' % settings.get_addr_name(addr))
            if message == r'\quit':
                nickname = settings.get_addr_name(addr)
                self.chatPanel.insert(tk.END, nickname + ' left chat room\n')
                self.__clientsDict[addr].quit()
                del self.__clientsDict[addr]
            # messageWords = re.split(r'\s+', message)
            # if settings.gameThread != None:
            #     if message == r'\gameover':
            #         self.clear_message()
            #         settings.gameThread = None
            #         print('Game shut down')
            #         return
            #     self.__queue.put(message)
            #     logging.info('put %s into the queue' % message)
            # else:
            #     if messageWords[0] == r'\janken':
            #         print('Received a game request %s (%s rounds) from %s. Accept (y/n)?' % (message, messageWords[1], self.get_nickname()))
            #         settings.gameThread = self
            #         self.__queue.put(message)
            #     elif messageWords[0] == r'\gameover':
            #         return
            #     else:
            #         print('Received strange command: %s' % message)
            pass

        else:
            nickname = settings.get_addr_name(addr)
            self.chatPanel.insert(tk.END, nickname + ':> ' + message + '\n')


    def say(self):
        message = self.messageInput.get()
        self.messageInput.delete(0,tk.END)
        if message != '':
            self.chatPanel.insert(tk.END, settings.username + ':> ' + message + '\n')
            for addr in self.__clientsDict:
                logging.info('Try to send message %s to %s' % (message, addr[0]))
                self.__clientsDict[addr].send_message(message)

    def quit(self):
        for clientThread in self.__clientsDict.values():
            clientThread.send_message(r'\quit')
            clientThread.quit()
        super().quit()



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


    # def get_clients_num(self):
    #     return len(self.__clientsDict)
