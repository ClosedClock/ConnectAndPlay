from tkinter import *
import threading
import time

class Board(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.length = 10
        self.createWidgets()


    def createWidgets(self):
        # self.title = Label(self, text='This is a board')
        # self.title.pack()

        self.buttons = [[None for x in range(self.length)] for x in range(self.length)]
        for i in range(self.length):
            for j in range(self.length):
                self.buttons[i][j] = Button(self, command=self.botton_func)
                self.buttons[i][j].config(height=10, width=5)
                self.buttons[i][j].grid(row=i, column=j)

    def botton_func(self):
        # subThread = threading.Thread(target=self.counting)
        # subThread.start()
        app = Subboard()
        print('created')
        # 设置窗口标题:
        # app.master.title('subboard')
        # 主消息循环:
        app.mainloop()

    def counting(self):
        count = 0
        while count < 20:
            print(count)
            count += 1
            time.sleep(2)

class Subboard(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.helloLabel = Label(self, text='Hello, world!')
        self.helloLabel.pack()
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()


def thread_stuff():
    app = Board()
    # 设置窗口标题:
    app.master.title('board')
    # 主消息循环:
    app.mainloop()


# subThread = threading.Thread(target=thread_stuff)
# subThread.start()
# subThread.join()
thread_stuff()