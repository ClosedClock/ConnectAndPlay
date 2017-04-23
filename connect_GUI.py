import tkinter as tk
from idlelib.WidgetRedirector import WidgetRedirector
import logging
from queue import Queue
import threading
import socket
from tkinter import messagebox
import settings


# class MemberListbox(tk.Listbox):
#     def __init__(self, master, **kw):
#         super().__init__(master, kw)
#         self.__memberDict = {}

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
        username = self.master.get_username()
        self.memberAddrDict = {username: 'MYSELF'}
        self.memberNameDict = {'MYSELF': username}
        self.memberListbox.insert(tk.END, username)
        logging.info('memberListbox created')

        self.challengeButton = tk.Button(self, text='Challenge', command=self.challenge_member)
        self.challengeButton.grid(row=1, column=2, sticky='N')

        self.inputText = tk.Text(self, width=60, height=3)
        self.inputText.grid(row=2, column=0, columnspan=3)
        self.inputText.bind('<Return>', self.say)
        logging.info('Widgets created')

    def get_input_content(self):
        content = self.inputText.get(1.0, tk.END)
        self.inputText.delete(1.0, tk.END)
        return content

    def print_to_chatPanel(self, content, speaker=None):
        if speaker == None:
            self.chatPanel.insert(tk.END, content + '\n')
            return
        self.chatPanel.insert(tk.END, speaker + ':> ' + content)

    def get_username(self):
        return self.memberNameDict['MYSELF']

    def add_member(self, addr):
        if addr == 'SERVER':
            name = self.master.get_friendList()[self.serverAddr[0]]
        else:
            if type(addr) != tuple:
                addr = self.str_to_addr(addr)
            name = self.master.get_friendList()[addr[0]]

        if name in self.memberAddrDict:
            i = 1
            while True:
                newName = name + '(' + str(i) + ')'
                if newName not in self.memberAddrDict:
                    self.memberAddrDict[newName] = addr
                    self.memberNameDict[addr] = newName
                    self.memberListbox.insert(tk.END, newName)
                    break
                i += 1
        else:
            self.memberAddrDict[name] = addr
            self.memberNameDict[addr] = name
            self.memberListbox.insert(tk.END, name)

    def delete_member(self, addr):
        name = self.memberNameDict[addr]
        del self.memberAddrDict[name]
        del self.memberNameDict[addr]

        for i in range(self.memberListbox.size()):
            if self.memberListbox.get(i) == name:
                self.memberListbox.delete(i)
                return
        logging.warning('Trying to delete nonexistent member from memberListbox!')

    def selected_member(self):
        name = self.memberListbox.get(tk.ACTIVE)
        addr = self.memberAddrDict[name]
        return (name, addr)

    def delete_all_members(self):
        self.memberAddrDict.clear()
        self.memberNameDict.clear()
        self.memberListbox.delete(0, tk.END)


class ConnectGUI(ChatGUI):
    def __init__(self, master):
        super().__init__(master)
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.__isRunning = True
        self.__gameDict = {}
        self.isServer = None
        logging.info('ConnectGUI initialization finished.')

    def isRunning(self):
        return self.__isRunning

    def str_to_addr(self, str):
        if str == 'ALL' or str == '' or str == 'SERVER':
            return str
        parts = str.split(':')
        ip = parts[0]
        host = int(parts[1])
        return (ip, host)

    def addr_to_str(self, addr):
        return addr[0] + ':' + str(addr[1])

    def update_member_with_username(self, herUsername, addr):
        ip = addr[0]
        if ip not in self.master.get_friendList():
            self.master.add_to_friendList(herUsername, ip)

    def send_message(self, command, target, content, sender=None):
        # TODO: 目前会调用ListenThread类,但是其实用sock就行了, 以后改
        if type(command) is not str:
            logging.warning('Wrong format in send_message!')
            return
        if type(content) is not str:
            content = str(content)

        if self.isServer:
            if sender == None:
                sender = 'SERVER'
            elif type(sender) is tuple:
                sender = self.addr_to_str(sender)
            message = command + '\000' + sender + '\000' + content + '\001'
            self.get_listen_thread_by_addr(target).send_message(message)
        else:
            if type(target) is tuple:
                target = self.addr_to_str(target)
            message = command + '\000' + target + '\000' + content + '\001'
            self.get_listen_thread().send_message(message)

    def has_game_with(self, addr, gameName):
        if addr in self.__gameDict:
            if gameName in self.__gameDict[addr]:
                return True
        return False

    def add_game_with(self, addr, gameName, game):
        if addr not in self.__gameDict:
            self.__gameDict[addr] = {}
        self.__gameDict[addr][gameName] = game

    def game_with(self, addr, gameName):
        try:
            return self.__gameDict[addr][gameName]
        except:
            return None

    def delete_game_with(self, addr, gameName):
        del self.__gameDict[addr][gameName]

    def challenge_member(self):
        name, addr = self.selected_member()
        if addr == 'MYSELF':
            return
        challengeToplevel = ChallengeToplevel(self, name, addr)






    def quit(self):
        logging.info('Set the isRunning flag of GUI to False')
        self.__isRunning = False
        self.master.isInChatroom = False
        self.destroy()


class ListenThread(threading.Thread):
    def __init__(self, master, sock, addr):
        logging.info('Initializing a ListenThread object')
        super().__init__()
        self.master = master
        self.__addr = addr
        self.__sock = sock
        self.__queue = Queue()
        self.__isRunning = True
        logging.info('A ListenThread object created')

    def run(self):
        emptyStrCounter = 0
        while self.__isRunning and emptyStrCounter < 50:
            try:
                message = self.__sock.recv(1024).decode('utf-8')
                logging.info(r'ListenThread got message "%s"' % message)
                if message == '':
                    emptyStrCounter += 1
                    continue
                else:
                    emptyStrCounter = 0
            except socket.timeout:
                continue
            messages = message.split('\001')
            for oneMessage in messages:
                if oneMessage != '':
                    logging.info('ListenThread is putting oneMessage %s into the queue' % oneMessage)
                    # self.__queue.put(oneMessage)
                    self.master.deal_message(self.__addr, oneMessage)
        self.__sock.close()
        logging.info('ListenThread closed')

    def get_message(self):
        return self.__queue.get(False)

    def has_message(self):
        return not self.__queue.empty()

    def send_message(self, message):
        self.__sock.send(message.encode('utf-8'))

    def isRunning(self):
        return self.__isRunning

    def quit(self):
        # TODO: 这里client退出时会调用两次, 以后需要检查
        logging.info('Set the ListenThread isRunning flag to False')
        # self.__sock.send(r'\quit'.encode('utf-8'))
        self.__isRunning = False


class ChallengeToplevel(tk.Toplevel):
    def __init__(self, master, name, addr):
        super().__init__(master)
        self.name = name
        self.addr = addr
        self.infoLabel = tk.Label(self, text='Please choose the game you want to play with %s' % name)
        self.infoLabel.grid(row=0, column=0, columnspan=2)
        self.gameNameLabel = tk.Label(self, text='Game Name:')
        self.gameNameLabel.grid(row=1, column=0, sticky='E')
        self.gameOptionVariable = tk.StringVar()
        self.gameOptionVariable.trace('w', self.selection_changed)
        self.gameOptionMenu = tk.OptionMenu(self, self.gameOptionVariable, *settings.gameDict.keys())
        self.gameOptionMenu.grid(row=1, column=1, sticky='W')
        self.confirmButton = tk.Button(self, text='Confirm', command=self.confirm)
        self.confirmButton.grid(row=3, column=0, columnspan=2)

    def selection_changed(self, *args):
        try:
            self.roundsChooseLabel.destroy()
            self.roundsChooseSpinbox.destroy()
        except:
            pass
        gameName = self.gameOptionVariable.get()
        maxRounds = settings.gameDict[gameName].maxRounds
        if maxRounds == 1:
            return
        self.roundsChooseLabel = tk.Label(self, text='Game Rounds:')
        self.roundsChooseLabel.grid(row=2, column=0, sticky='E')
        self.roundsChooseSpinbox = tk.Spinbox(self, from_=1, to=maxRounds)
        self.roundsChooseSpinbox.grid(row=2, column=1, sticky='W')

    def confirm(self):
        gameName = self.gameOptionVariable.get()
        if gameName == '':
            return
        try:
            rounds = self.roundsChooseSpinbox.get()
        except:
            rounds = 1
        if self.master.has_game_with(self.addr, gameName):
            messagebox.showwarning('Warning', 'You have already started %s with %s' % (gameName, self.name))
            return
        self.master.send_message('challenge', self.addr, gameName + ' ' + str(rounds))
        self.destroy()




class ReadOnlyText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")