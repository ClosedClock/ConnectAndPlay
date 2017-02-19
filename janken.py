from enum import Enum
import re
import tkinter as tk
import logging

from game import Game


class JankenGesture(Enum):
    ROCK = 0
    SCISSORS = 1
    PAPER = 2

class GameResult(Enum):
    DRAW = 0
    LOSE = 1
    WIN = 2


class Janken(Game):
    def __init__(self, master, rivalAddr, rounds):
        super().__init__(master, rivalAddr)
        self.__rounds = int(rounds)
        self.__currentRound = 1
        self.__resultList = []
        self.__rivalGesture = tk.IntVar()
        self.__rivalGesture.set(-1)
        self.__myGesture = -1
        self.create_widgets()

    def create_widgets(self):
        self.waitingLabel = tk.Label(self, text='Waiting for your rival...')

        self.resultFrame = tk.Frame(self)
        self.resultLabel1 = tk.Label(self.resultFrame)
        self.resultLabel1.pack()
        self.resultLabel2 = tk.Label(self.resultFrame)
        self.resultLabel2.pack()
        self.confirmButton = tk.Button(self.resultFrame, text='Confirm', command=self.next_turn)
        self.confirmButton.pack()

        self.chooseFrame = tk.Frame(self)
        self.roundLabel = tk.Label(self.chooseFrame, text='This is round %d' % self.__currentRound)
        self.roundLabel.grid(row=0, column=0, columnspan=3)
        self.infoLabel = tk.Label(self.chooseFrame, text='Please choose your gesture')
        self.infoLabel.grid(row=1, column=0, columnspan=3)
        self.rockButton = tk.Button(self.chooseFrame, text='Rock', command=lambda: self.do_gesture(0))
        self.rockButton.grid(row=2, column=0)
        self.rockButton = tk.Button(self.chooseFrame, text='Scissors', command=lambda: self.do_gesture(1))
        self.rockButton.grid(row=2, column=0)
        self.rockButton = tk.Button(self.chooseFrame, text='Paper', command=lambda: self.do_gesture(2))
        self.rockButton.grid(row=2, column=0)
        self.chooseFrame.pack()

    def do_gesture(self, gestureNumber):
        self.__myGesture = gestureNumber
        self.send_info(str(gestureNumber))
        self.chooseFrame.pack_forget()
        if self.__rivalGesture == -1:
            self.waitingLabel.pack()
        else:
            self.show_round_result()

    # def play(self):
    #     if not self.isRunning():
    #         return
    #     self.__currentRoundNum = 1
    #     while self.__currentRoundNum <= self.__totalRoundNum:
    #         print('Round %d' % self.__currentRoundNum)
    #         self.one_round()
    #         self.__currentRoundNum += 1
    #     self.show_result()


    def show_result(self):
        winNum = 0
        loseNum = 0
        for result in self.__resultList:
            if result == GameResult.WIN:
                winNum += 1
            elif result == GameResult.LOSE:
                loseNum += 1
        tk.Label(text='Win: %d, Lose: %d, Draw: %d' % (winNum, loseNum, self.__rounds - winNum - loseNum)).pack()
        tk.Label(text='Confirm', command=self.quit).pack()

    #
    # def one_round(self):
    #     inputStr = input("Choose your gesture (0-Rock, 1-Scissors, 2-Paper): ")
    #     while inputStr not in ('0', '1', '2'):
    #         inputStr = input("Your input is not of a correct form, please enter again: ")
    #     myGesture = JankenGesture(int(inputStr))
    #     self.send_message('\janken ' + inputStr)
    #     opponentGesture = self.get_opponent_gesture()
    #     result = self.round_result(myGesture, opponentGesture)
    #     self.__resultList.append(result)


    def received_info(self, rivalGesture):
        self.__rivalGesture = rivalGesture

    def received_rival_gesture(self):
        if self.__myGesture != -1:
            self.waitingLabel.pack_forget()
            self.next_turn()

    def show_round_result(self):
        myGesture = self.__myGesture
        self.__myGesture = -1
        rivalGesture = self.__rivalGesture.get()
        self.__rivalGesture.set(-1)
        result = GameResult((myGesture - rivalGesture) % 3)
        self.__resultList.append(result)
        gestureDisplayDict = {0: 'Rock', 1: 'Scissors', 2: 'Paper'}
        resultDisplayDict = {GameResult.DRAW: ('-X-', 'Draw'),
                             GameResult.WIN: ('-->', 'You Win!'),
                             GameResult.LOSE: ('<--', 'You Lose')}
        resultInfo = '%s: %s %s %s :%s' % (self.myName, gestureDisplayDict[myGesture],
                                           resultDisplayDict[result][0], gestureDisplayDict[rivalGesture],
                                           self.rivalName)
        self.resultLabel1.config(text=resultInfo)
        self.resultLabel2.config(text=resultDisplayDict[result][1])
        self.waitingLabel.pack_forget()
        self.resultFrame.pack()

    def next_turn(self):
        self.resultFrame.pack_forget()
        self.__currentRound += 1
        if self.__currentRound > self.__rounds:
            self.show_result()
            return
        self.infoLabel.config(text='This is round %d' % self.__currentRound)
        self.chooseFrame.pack()

