import socket
import threading
import logging
import settings

from connect_GUI import ConnectGUI, ListenThread


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
        self.__addr = (socket.gethostbyname(socket.gethostname()), settings.PORT)
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

            for existedAddr in self.__clientsDict:
                self.__clientsDict[existedAddr].send_message('new_member' + '\000\000' + self.addr_to_str(addr))
            self.add_member(addr)
            self.__clientsDict[addr] = ListenThread(sock)
            for existedAddr in self.__clientsDict:
                if existedAddr != addr:
                    self.__clientsDict[addr].send_message('new_member' + '\000\000' + self.addr_to_str(existedAddr))

            self.__clientsDict[addr].start()
            self.print_to_chatPanel('Accept new connection from %s...' % self.get_name_of_addr(addr))
            print('Accept new connection from %s...' % self.get_name_of_addr(addr))
        logging.info('Waiting thread closed')
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

    def deal_message(self, sender, message):
        '''
        处理消息, 根据addr的不同会有不同的处理
        :param sender: 消息发送方的地址
        :param message: 消息
        :return:
        '''
        messageWords = message.split('\000')
        try:
            command = messageWords[0]
            target = self.str_to_addr(messageWords[1])
            content = messageWords[2]
        except IndexError:
            logging.warning('Received message with wrong format: %s' % message)
            return False

        if command == 'quit':
            logging.info(str(sender) + ' sent a quit message')
            nickname = self.get_name_of_addr(sender)
            self.print_to_chatPanel(nickname + ' left chat room')
            self.__clientsDict[sender].quit()
            return True

        elif command == 'say':
            if target == 'ALL':
                nickname = self.get_name_of_addr(sender)
                self.print_to_chatPanel(content, nickname)
                transitMessage = 'say' + '\000' + self.addr_to_str(sender) + '\000' + content
                for addr in self.__clientsDict:
                    if addr == sender:
                        continue
                    logging.info('Try to send message %s to %s' % (transitMessage, addr))
                    self.__clientsDict[addr].send_message(transitMessage)
            else:
                logging.warning('Target of say is not ALL!')
                return False

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

        return False


    def say(self, event):
        '''
        从输入框读取消息然后发送到全体成员
        :return:
        '''
        content = self.get_input_content()
        if content != '':
            self.print_to_chatPanel(content, self.get_username())
            for addr in self.__clientsDict:
                logging.info('Try to send message %s to %s' % (content, addr[0]))
                self.__clientsDict[addr].send_message('say' + '\000' + self.addr_to_str(self.__addr) + '\000' + content)
        return 'break'


    def challenge_member(self):
        pass


    def quit(self):
        '''
        重载了关闭按钮的函数, 会发送给所有client退出命令
        :return:
        '''
        try:
            for clientThread in self.__clientsDict.values():
                try:
                    clientThread.send_message('quit\000\000')
                except OSError:
                    pass
                clientThread.quit()
        except AttributeError:
            pass
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

