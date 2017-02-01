import settings
import queue
import logging


class Game(object):
    def __init__(self, isChallenger, *args):
        self.__isChallenger = isChallenger
        if isChallenger:
            if len(args) == 0:
                ip = None
            elif len(args) == 1:
                ip = args[0]
            else:
                raise SyntaxError
            self.__thread = settings.get_connect_thread(ip)
            settings.gameThread = self.__thread
        else:
            self.__thread = settings.gameThread
        self.__nickname = self.__thread.get_nickname()
        self.__isRunning = True
        self.__username = settings.username

    def invite(self, message):
        self.send_message(message)
        try:
            reply = self.get_message(10)
        except queue.Empty:
            print('No response')
            self.__isRunning = False
            return
        logging.info('Reply is \"%r\"' % reply)
        if reply == r'\yes':
            print('Requist accepted. Game start!')
        else:
            print('Requist refused')
            self.__isRunning = False

    def send_message(self, message):
        self.__thread.send_message(message)

    def get_message(self, timeout=None):
        return self.__thread.get_message(timeout)

    def nickname(self):
        return self.__nickname

    def username(self):
        return self.__username

    def isChallenger(self):
        return self.__isChallenger

    def isRunning(self):
        return self.__isRunning

    def game_over(self):
        self.send_message('\gameover')