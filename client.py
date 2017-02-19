import logging

import settings
from connect_GUI import ConnectGUI, ListenThread
from tkinter import messagebox


class ClientGUI(ConnectGUI):
    def __init__(self, master, sock, addr):
        logging.info('Initializing a ClientGUI object')
        super().__init__(master)
        self.isServer = False
        self.__gameDict = {addr: {}}
        self.serverAddr = addr
        print('serverAddr is\n')
        print(self.serverAddr)

        self.__tServer = ListenThread(sock)
        self.__tServer.start()
        self.send_message('hello', 'SERVER', self.get_username())
        self.after(100, self.check_message)
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
            logging.info('command is %s' % command)
            sender = self.str_to_addr(messageWords[1])
            logging.info('sender is %s' % messageWords[1])
            content = messageWords[2]
            logging.info('content is %s' % content)
        except IndexError:
            logging.warning('Received message with wrong format: %s' % message)
            return False

        if command == 'quit':
            self.delete_all_members()
            self.print_to_chatPanel('Chat room closed.')
            self.__tServer.quit()
            return True

        elif command == 'hello':
            logging.info('Received hello message from %s' % content)
            herUsername = content
            self.update_member_with_username(herUsername, self.serverAddr)
            self.add_member('SERVER')

        elif command == 'existed_member' or command == 'new_member':
            logging.info('Adding new member. Address: %s, username: %s' % (sender, content))
            herUsername = content
            self.update_member_with_username(herUsername, sender)
            self.add_member(sender)
            if command == 'new_member':
                nickname = self.memberNameDict[sender]
                self.print_to_chatPanel(nickname + ' entered chat room')

        elif command == 'member_leave':
            nickname = self.memberNameDict[sender]
            logging.info('Member %s left' % nickname)
            self.delete_member(sender)
            self.print_to_chatPanel(nickname + ' left chat room')

        elif command == 'say':
            nickname = self.memberNameDict[sender]
            self.print_to_chatPanel(content, nickname)

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
                self.send_message('reply_challenge', sender, 'yes')
                newGame = settings.gameDict[gameName].function(self, sender, *gameInfo[1:])
                self.add_game_with(sender, gameName, newGame)
            else:
                self.send_message('reply_challenge', sender, 'no')

        elif command == 'reply_challenge':
            if content == 'no':
                pass
                return
            if content == 'yes':
                gameInfo = content.split()
                gameName = gameInfo[0]
                newGame = settings.gameDict[gameName].function(*gameInfo[1:])
                self.add_game_with(sender, gameName, newGame)

        elif command == 'game_over':
            self.game_with(sender, content).received_info('game_over')
            self.delete_game_with(sender, content)

        elif command == 'game':
            gameInfo = content.split()
            gameName = gameInfo[0]
            if not self.has_game_with(sender, gameName):
                logging.warning('Got game message with no game being played!')
                return
            self.game_with(sender, gameName).received_info(*gameInfo[1:])

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
            self.print_to_chatPanel(content, self.memberNameDict['MYSELF'])
            self.send_message('say', 'ALL', content)
        return 'break'

    def get_listen_thread(self):
        return self.__tServer

    def quit(self):
        try:
            self.send_message('quit', 'SERVER', '')
        except OSError:
            pass
        self.__tServer.quit()
        super().quit()

