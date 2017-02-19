import settings
import queue
import logging
import tkinter as tk


class Game(tk.Toplevel):
    def __init__(self, master, rivalAddr):
        super().__init__(master)
        self.__myName = self.master.get_username()
        self.__rivalName = self.master.memberNameDict[rivalAddr]
        self.__rivalAddr = rivalAddr
        self.__isServer = self.master.isServer
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

    def received_info(self, *gameInfo):
        logging.warning('received_info has not been implemented!')

    def quit(self):
        self.master.send_message('game_over', self.__rivalAddr, self.__class__.__name__)
        self.destroy()


class TurnBasedGame(Game):
    def __init__(self, master, rivalAddr):
        super().__init__(master, rivalAddr)
        self.turnIsDecided = False
        self.isMyTurn = False

    def turn_over(self):
        logging.warning('turn_over has not been implemented!')
