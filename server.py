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
    '''
    创建聊天室时ServerGUI被创建
    左上是聊天界面
    右上是在线列表, 点击列表应该可以发起对战, 单独点击菜单里的游戏应该弹出选择对手的窗口, 可以选择AI
    下方是发送框和发送按钮
    '''
    def __init__(self, master, sock):
        logging.info('Initializing a ServerGUI object')
        super().__init__(master)

        self.__clientsDict = {}
        #TODO: dict max length may be adjusted later
        self.__sock = sock
        # self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.__sock.settimeout(0.3)
        # self.__sock.bind((host, port))
        # self.__sock.listen(5)

        self.__serverThread = threading.Thread(target=self.waiting)
        self.__serverThread.start()
        logging.info('A ServerGUI object created')

    def waiting(self):
        '''
        监听连接, 为每个连接创建一个thread
        通过设置isRunning到false来关闭
        :return:
        '''
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
        '''
        检查每个slave thread有没有收到消息, 处理消息(如果很耗时比如游戏就应该再建立一个线程)
        检查完后将自己加入到100ms后的mainloop里
        :return:
        '''
        quitClientsList = []
        for addr, clientThread in self.__clientsDict.items():
            while clientThread.has_message():
                message = clientThread.get_message()
                logging.info('Got message from %s: %s' % (addr, message))
                clientIsGone = self.deal_message(addr, message)
                if clientIsGone:
                    quitClientsList.append(addr)
        for addr in quitClientsList:
            del self.__clientsDict[addr]
        self.after(100, self.check_message)

    def deal_message(self, addr, message):
        '''
        处理消息, 根据addr的不同会有不同的处理
        :param addr: 消息发送方的地址
        :param message: 消息
        :return:
        '''
        if message[0] == '\\':
            logging.info('This is a command from: %s' % settings.get_addr_name(addr))
            if message == r'\quit':
                nickname = settings.get_addr_name(addr)
                self.chatPanel.insert(tk.END, nickname + ' left chat room\n')
                self.__clientsDict[addr].quit()
                return True
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
            #         print('Received a game request %s (%s rounds) from %s. Accept (y/n)?'
            # % (message, messageWords[1], self.get_nickname()))
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

        return False


    def say(self):
        '''
        从输入框读取消息然后发送到全体成员
        :return:
        '''
        message = self.messageInput.get()
        self.messageInput.delete(0,tk.END)
        if message != '':
            self.chatPanel.insert(tk.END, settings.username + ':> ' + message + '\n')
            for addr in self.__clientsDict:
                logging.info('Try to send message %s to %s' % (message, addr[0]))
                self.__clientsDict[addr].send_message(message)

    def quit(self):
        '''
        重载了关闭按钮的函数, 会发送给所有client退出命令
        :return:
        '''
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
