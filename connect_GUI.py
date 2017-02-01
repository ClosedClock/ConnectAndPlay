import tkinter as tk
from idlelib.WidgetRedirector import WidgetRedirector
import logging



class ConnectGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.info('Created root for ClientGUI')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.__isRunning = True
        logging.info('Going to create widgets')
        self.create_widgets()

        self.after(100, self.check_message)


    def create_widgets(self):
        self.messageInput = tk.Entry(self)
        self.messageInput.pack()
        self.sendButton = tk.Button(self, text='Send', command=self.say)
        self.sendButton.pack()

        self.chatPanel = ReadOnlyText(self, width=46)
        self.chatPanel.pack(side='left',fill='y')

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='right', fill='y')

        scrollbar.config(command=self.chatPanel.yview)
        self.chatPanel.config(yscrollcommand=scrollbar.set)

    def isRunning(self):
        return self.__isRunning

    def quit(self):
        logging.info('Set the isRunning flag to False')
        self.__isRunning = False
        self.destroy()



class ReadOnlyText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")