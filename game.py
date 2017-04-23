import settings
import queue
import logging
import tkinter as tk
import threading
from queue import Queue

class GameHelperThread(threading.Thread):
    def __init__(self, master, queue):
        logging.info('Initializing a GameHelperThread object')
        super().__init__()
        self.master = master
        self.__queue = queue
        self.__isRunning = True
        logging.info('A GameHelperThread object created')

    def run(self):
        while self.__isRunning:
            try:
                infoList = self.__queue.get(timeout=0.3)
            except queue.Empty:
                continue
            logging.info('GameHelperThread got an info %s' % infoList)
            self.master.deal_info(*infoList)
        logging.info('GameHelperThread closed')

    def quit(self):
        logging.info('Set the GameHelperThread isRunning flag to False')
        self.__isRunning = False


class Game(tk.Toplevel):
    def __init__(self, master, rivalAddr):
        super().__init__(master)
        self.__myName = self.master.get_username()
        self.__rivalName = self.master.memberNameDict[rivalAddr]
        self.__rivalAddr = rivalAddr
        self.__isServer = self.master.isServer
        self.infoQueue = Queue()
        self.gameHelper = GameHelperThread(self, self.infoQueue)
        self.gameHelper.start()
        self.protocol('WM_DELETE_WINDOW', self.quit)
        pass

    @property
    def myName(self):
        return self.__myName

    @property
    def rivalName(self):
        return self.__rivalName

    @property
    def isServer(self):
        return self.__isServer

    def send_info(self, info):
        self.master.send_message('game', self.__rivalAddr, self.__class__.__name__ + ' ' + info)

    def deal_info(self, *infoList):
        logging.warning('received_info has not been implemented!')

    def quit(self):
        self.master.send_message('game_over', self.__rivalAddr, self.__class__.__name__)
        self.gameHelper.quit()
        self.master.delete_game_with(self.__rivalAddr, self.__class__.__name__)
        self.destroy()


class TurnBasedGame(Game):
    def __init__(self, master, rivalAddr):
        super().__init__(master, rivalAddr)
        self.turnIsDecided = False
        self.isMyTurn = False

    def turn_over(self):
        logging.warning('turn_over has not been implemented!')
