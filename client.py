import logging

import settings
from connect_GUI import ConnectGUI, ListenThread


class ClientGUI(ConnectGUI):
    def __init__(self, master, sock, addr):
        logging.info('Initializing a ClientGUI object')
        super().__init__(master)
        # self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.__sock.settimeout(0.3)
        # self.__sock.connect(addr)
        self.__tServer = ListenThread(sock)
        self.__tServer.start()
        self.__serverAddr = addr
        self.__connectedDict = {addr: {}}
        logging.info('A ClientGUI object created')

    def check_message(self):
        # if not self.isConnecting():
        #     return
        while self.__tServer.has_message():
            message = self.__tServer.get_message()
            logging.info('Got message from queue %s' % message)
            serverIsGone = self.deal_message(message)
            if serverIsGone:
                pass
        self.after(100, self.check_message)

    def deal_message(self, message):
        messageWords = message.split('\000')
        try:
            command = messageWords[0]
            sender = self.str_to_addr(messageWords[1])
            content = messageWords[2]
        except IndexError:
            logging.warning('Received message with wrong format: %s' % message)
            return False

        if command == 'quit':
            self.print_to_chatPanel('Chat room closed.')
            self.__tServer.quit()

        elif command == 'add_member':
            addr = self.str_to_addr(content)
            self.__connectedDict[addr] = {}
            self.add_member(addr)

        elif command == 'say':
            nickname = self.get_name_of_addr(sender)
            self.print_to_chatPanel(content, nickname)

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

    def say(self, event):
        '''
        目前发给服务器后就结束了, 以后需要用服务器广播到所有client
        :return:
        '''
        if not self.__tServer.isRunning():
            self.print_to_chatPanel('Chat room closed.')
            return
        content = self.get_input_content()
        if content != '':
            self.print_to_chatPanel(content, self.get_username())
            self.__tServer.send_message('say' + '\000' + 'ALL' + '\000' + content)
        return 'break'

    def challenge_member(self):
        pass

    def quit(self):
        try:
            self.__tServer.send_message('quit\000\000')
        except OSError:
            pass
        self.__tServer.quit()
        super().quit()

