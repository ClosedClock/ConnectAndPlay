import socket
import threading
import re
import tkinter as tk
from idlelib.WidgetRedirector import WidgetRedirector
import logging
from queue import Queue
from tkinter import *

import settings

class ConnectThread(threading.Thread):
    def __init__(self, sock, addr):
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

    def deal_message(self, message):
        if message[0] == '\\':
            logging.info('This is a command from: %s' % self.get_nickname())
            messageWords = re.split(r'\s+', message)
            if settings.gameThread != None:
                if message == r'\gameover':
                    self.clear_message()
                    settings.gameThread = None
                    print('Game shut down')
                    return
                self.__queue.put(message)
                logging.info('put %s into the queue' % message)
            else:
                if messageWords[0] == r'\janken':
                    print('Received a game request %s (%s rounds) from %s. Accept (y/n)?' % (message, messageWords[1], self.get_nickname()))
                    settings.gameThread = self
                    self.__queue.put(message)
                elif messageWords[0] == r'\gameover':
                    return
                else:
                    print('Received strange command: %s' % message)

        else:
            #print(command)
            print('%s:> %s' % (self.get_nickname(), message))

    def get_message(self, timeout=None):
        return self.__queue.get(True, timeout)


    def send_message(self, message):
        self.__sock.send(message.encode('utf-8'))


    def quit(self):
        self.__isRunning = False


    def get_connected_addr(self):
        return self.__addr


    def clear_message(self):
        self.__queue.queue.clear()





class ConnectGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.info('Created root for ClientGUI')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.__isRunning = True
        logging.info('Going to create widgets')
        self.create_widgets()
        logging.info('Finished initialization')

        self.after(100, self.check_message)


    def create_widgets(self):
        self.messageInput = tk.Entry(self)
        self.messageInput.pack()
        self.sendButton = tk.Button(self, text='Send', command=self.say)
        self.sendButton.pack()

        self.chatPanel = ReadOnlyText(self, width=46)
        self.chatPanel.pack(side='left',fill='y')

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='right', fill='y')

        scrollbar.config(command=self.chatPanel.yview)
        self.chatPanel.config(yscrollcommand=scrollbar.set)

    def receive_message(self):
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
                self.__queue.put(message)
            except socket.timeout:
                continue
            if message == r'\quit':
                break
        sock.send(br'\quit')
        sock.close()

    def send_message(self):
        pass

    def isRunning(self):
        return self.__isRunning

    def quit(self):
        self.__isRunning = False
        self.destroy()



class ReadOnlyText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")