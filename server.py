import socket
import threading
import logging
from tkinter import messagebox
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
        self.isServer = True
        self.__connectDict = {}
        self.__usernameDict = {}
        self.__sock = sock
        # self.__addr = (socket.gethostbyname(socket.gethostname()), settings.PORT)
        self.__serverThread = threading.Thread(target=self.waiting)
        self.__serverThread.start()
        # self.after(100, self.check_message)
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

            self.__connectDict[addr] = ListenThread(self, sock, addr)
            self.send_message('hello', addr, self.get_username())
            for existedAddr in self.__connectDict:
                if existedAddr != addr:
                    logging.info('Sending existed_member message of %s to %s' % (existedAddr, addr))
                    self.send_message('existed_member', addr, self.__usernameDict[existedAddr], existedAddr)

            self.__connectDict[addr].start()
        self.__sock.close()
        logging.info('Waiting thread closed')

    # 这个函数暂时不使用,改为用ListenThread来直接调用deal_message
    def check_message(self):
        '''
        检查每个slave thread有没有收到消息, 处理消息(如果很耗时比如游戏就应该再建立一个线程)
        检查完后将自己加入到100ms后的mainloop里
        :return:
        '''
        quitClientsList = []
        for addr, clientThread in self.__connectDict.items():
            while clientThread.has_message():
                message = clientThread.get_message()
                logging.info('Got message from %s: %s' % (addr, message))
                clientIsGone = self.deal_message(addr, message)
                if clientIsGone:
                    quitClientsList.append(addr)
        for addr in quitClientsList:
            del self.__connectDict[addr]
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
            logging.info('command is %s' % command)
            target = self.str_to_addr(messageWords[1])
            logging.info('target is %s' % messageWords[1])
            content = messageWords[2]
            logging.info('content is %s' % content)
        except IndexError:
            logging.warning('Received message with wrong format: %s' % message)
            return False

        if target != 'SERVER' and target != 'ALL':
            self.send_message(command, target, content, sender)
            return

        if command == 'quit':
            logging.info(str(sender) + ' sent a quit message')
            nickname = self.memberNameDict[sender]
            for addr in self.__connectDict:
                if addr != sender:
                    self.send_message('member_leave', addr, '', sender)
            self.delete_member(sender)
            self.print_to_chatPanel(nickname + ' left chat room')
            self.__connectDict[sender].quit()
            return True

        elif command == 'hello':
            logging.info('Received hello message from %s' % content)
            herUsername = content
            self.__usernameDict[sender] = herUsername
            self.update_member_with_username(herUsername, sender)
            for existedAddr in self.__connectDict:
                if existedAddr != sender:
                    logging.info('Sending new_member message of %s to %s' % (sender, existedAddr))
                    self.send_message('new_member', existedAddr, herUsername, sender)
            self.add_member(sender)
            self.print_to_chatPanel('%s entered chat room' % self.memberNameDict[sender])
            # print('Accept new connection from %s...' % self.memberNameDict[sender])

        elif command == 'say':
            if target == 'ALL':
                nickname = self.memberNameDict[sender]
                self.print_to_chatPanel(content, nickname)
                for addr in self.__connectDict:
                    if addr == sender:
                        continue
                    self.send_message('say', addr, content, sender)
            else:
                logging.warning('Target of say is not ALL!')
                return False

        elif command == 'challenge':
            nickname = self.memberNameDict[sender]
            gameInfo = content.split()
            gameName = gameInfo[0]
            if self.has_game_with(sender, gameName):
                logging.warning('Got challenged by a person with existed game!')
                return
            rounds = int(gameInfo[1])
            answer = messagebox.askquestion('Here comes a new challenger!',
                                            '%s wants to play %s for %d rounds with you. Do you want to accept?'
                                            % (nickname, gameName, rounds), icon='info')
            if answer == 'yes':
                # if self.has_game_with(sender, gameName):
                #     logging.warning('Got challenged by a person with existed game!')
                #     return
                self.send_message('reply_challenge', sender, content)
                newGame = settings.gameDict[gameName].function(self, sender, *gameInfo[1:])
                self.add_game_with(sender, gameName, newGame)
            else:
                self.send_message('reply_challenge', sender, 'no')

        elif command == 'reply_challenge':
            if content == 'no':
                pass
                return
            else:
                gameInfo = content.split()
                gameName = gameInfo[0]
                newGame = settings.gameDict[gameName].function(self, sender, *gameInfo[1:])
                self.add_game_with(sender, gameName, newGame)

        elif command == 'game_over':
            # TODO: 如果一个人关了另一个人无法欣赏结果. 如果改成另一个人不关, 可能会因为
            # TODO: 一边记录着有游戏,一边没有而造成bug (但似乎没有问题)
            try:
                self.game_with(sender, content).quit()
            except:
                pass
            # self.delete_game_with(sender, content)

        elif command == 'game':
            gameInfo = content.split()
            gameName = gameInfo[0]
            if not self.has_game_with(sender, gameName):
                logging.warning('Got game message with no game being played!')
                return
            # self.game_with(sender, gameName).received_info(*gameInfo[1:])
            logging.info('Putting gameInfo %s into infoQueue' % gameInfo[1:])
            self.game_with(sender, gameName).infoQueue.put(gameInfo[1:])

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
            self.print_to_chatPanel(content, self.memberNameDict['MYSELF'])
            for addr in self.__connectDict:
                logging.info('Try to send message %s to %s' % (content, addr[0]))
                self.send_message('say', addr, content)
        return 'break'

    def get_listen_thread_by_addr(self, addr):
        return self.__connectDict[addr]

    def quit(self):
        '''
        重载了关闭按钮的函数, 会发送给所有client退出命令
        :return:
        '''
        try:
            for addr in self.__connectDict:
                try:
                    self.send_message('quit', addr, '')
                except OSError:
                    pass
                self.__connectDict[addr].quit()
        except AttributeError:
            pass
        super().quit()

    # def get_clients_addr(self):
    #     return self.__clientsDict.keys()
    #
    #
    # def get_slave_thread(self, ip=None):
    #     if len(self.__clientsDict) == 0:
    #         raise KeyError('No connection')
    #
    #     if ip == None:
    #         if len(self.__clientsDict) == 1:
    #             for k in self.__clientsDict:
    #                 return self.__clientsDict[k]
    #         else:
    #             raise KeyError('Address needed')
    #     else:
    #         for addr in self.__clientsDict:
    #             if addr[0] == ip:
    #                 return self.__clientsDict[addr]
    #         raise KeyError('Address not in clientDict when get_slave_thread')

