import tkinter as tk
from idlelib.WidgetRedirector import WidgetRedirector
import logging
from queue import Queue
import threading
import socket

class ChatGUI(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        logging.info('Going to create widgets')
        self.chatPanel = ReadOnlyText(self, width=40, height=20)
        self.chatPanel.grid(row=0, column=0, rowspan=2, sticky='WENS')

        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, rowspan=2, sticky='WNS')

        self.scrollbar.config(command=self.chatPanel.yview)
        self.chatPanel.config(yscrollcommand=self.scrollbar.set)

        self.memberListbox = tk.Listbox(self, width=10, height=10)
        self.memberListbox.grid(row=0, column=2, sticky='WEN')

        self.challengeButton = tk.Button(self, text='Challenge', command=self.challenge_member)
        self.challengeButton.grid(row=1, column=2, sticky='N')

        self.inputText = tk.Text(self, width=60, height=3)
        self.inputText.grid(row=2, column=0, columnspan=3)
        self.inputText.bind('<Return>', self.say)

    def get_input_content(self):
        content = self.inputText.get(1.0, tk.END)
        self.inputText.delete(1.0, tk.END)
        return content

    def print_to_chatPanel(self, content, speaker=None):
        if speaker == None:
            self.chatPanel.insert(tk.END, content + '\n')
            return
        self.chatPanel.insert(tk.END, speaker + ':> ' + content)

    def add_member(self, addr):
        self.memberListbox.insert(tk.END, addr)

    def delete_member(self, addr):
        for i in range(self.memberListbox.size()):
            if self.memberListbox.get(i) == addr:
                self.memberListbox.delete(i)
                return
        logging.warning('Trying to delete nonexistent member from memberListbox!')

    def selected_member(self):
        return self.memberListbox.get(tk.ACTIVE)

    def delete_all_members(self):
        self.memberListbox.delete(0, tk.END)


class ConnectGUI(ChatGUI):
    def __init__(self, master):
        super().__init__(master)
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.__isRunning = True
        self.after(100, self.check_message)

    def isRunning(self):
        return self.__isRunning

    def get_username(self):
        return self.master.get_username()

    def str_to_addr(self, str):
        if str == 'ALL' or str == '':
            return str
        parts = str.split(':')
        ip = parts[0]
        host = int(parts[1])
        return (ip, host)

    def addr_to_str(self, addr):
        return addr[0] + ':' + str(addr[1])

    def get_name_of_addr(self, addr):
        try:
            return self.master.get_friendList()[addr[0]]
        except:
            return self.addr_to_str(addr)


    def quit(self):
        logging.info('Set the isRunning flag to False')
        self.__isRunning = False
        self.master.isInChatroom = False
        self.destroy()


class ListenThread(threading.Thread):
    def __init__(self, sock):
        logging.info('Initializing a ServerSlaveThread object')
        super().__init__()
        self.__sock = sock
        self.__queue = Queue()
        self.__isRunning = True
        logging.info('A ServerSlaveThread object created')

    def run(self):
        emptyStrCounter = 0
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = self.__sock.recv(1024).decode('utf-8')
                logging.info(r'Got message "%s"' % message)
                if message == '':
                    emptyStrCounter += 1
                    continue
                else:
                    emptyStrCounter = 0
                logging.info('Putting message %s into the queue' % message)
            except socket.timeout:
                continue
            self.__queue.put(message)
        self.__sock.close()

    def get_message(self):
        return self.__queue.get(False)

    def has_message(self):
        return not self.__queue.empty()

    def send_message(self, message):
        self.__sock.send(message.encode('utf-8'))

    def isRunning(self):
        return self.__isRunning

    def quit(self):
        logging.info('Set the ServerSlaveThread isRunning flag to False')
        # self.__sock.send(r'\quit'.encode('utf-8'))
        self.__isRunning = False




class ReadOnlyText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")