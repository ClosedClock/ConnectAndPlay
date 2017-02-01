import socket
import tkinter as tk
from idlelib.WidgetRedirector import WidgetRedirector
from queue import Queue
import threading
import re

import settings
from settings import Mode, logging
from connect_thread import ConnectThread
from connect_thread import ConnectGUI


class ReadOnlyText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")


class ClientThread(ConnectThread):
    def __init__(self, addr):
        logging.info('Initializing a ServerThread object')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        sock.connect(addr)
        super().__init__(sock, addr)
        logging.info('A ServerThread object created')

    def run(self):
        print('Connected to %s' % self.get_nickname())
        super().run()
        settings.mode = Mode.NORMAL
        print('Connection to %s closed.' % self.get_nickname())

    def quit(self):
        logging.info('Set the ClientThread isRunning flag to False')
        super().quit()


class ClientGUI(ConnectGUI):
    def __init__(self, addr):
        super().__init__()
        logging.info('Created root for ClientGUI')
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.settimeout(0.3)
        self.__sock.connect(addr)
        self.__queue = Queue()
        self.__serverAddr = addr

        self.__isConnecting = True

        self.__clientThread = threading.Thread(target=self.receive_message)
        self.__clientThread.start()


    def receive_message(self):
        emptyStrCounter = 0
        sock = self.__sock
        while self.__isConnecting and emptyStrCounter < 50:
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

    def check_message(self):
        if not self.__isConnecting:
            return
        while not self.__queue.empty():
            message = self.__queue.get(False)
            logging.info('Got message from queue %s' % message)
            self.deal_message(message)
        self.after(100, self.check_message)

    def deal_message(self, message):
        if message[0] == '\\':
            logging.info('This is a command from: %s' % settings.get_addr_name(self.__serverAddr))
            if message == r'\quit':
                self.chatPanel.insert(tk.END, 'Chat room closed.\n')
                self.__isConnecting = False

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
            nickname = settings.get_addr_name(self.__serverAddr)
            self.chatPanel.insert(tk.END, nickname + ':> ' + message + '\n')

    def say(self):
        if not self.__isConnecting:
            self.chatPanel.insert(tk.END, 'Chat room closed.\n')
            return
        message = self.messageInput.get()
        self.messageInput.delete(0,tk.END)
        if message != '':
            self.chatPanel.insert(tk.END, settings.username + ':> ' + message + '\n')
            self.__sock.send(message.encode('utf-8'))


    def quit(self):
        if self.__isConnecting:
            self.__sock.send(r'\quit'.encode('utf-8'))
            self.__isConnecting = False
        super().quit()
