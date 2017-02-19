import tkinter as tk
from tkinter import messagebox
import socket
import json
import re
from functools import partial

import settings
from server import ServerGUI
from client import ClientGUI


class Application(tk.Tk):
    '''
    这个是初始的GUI, 包含所有别的.
    正在编写菜单栏, 菜单栏包含: 帮助, 设置, 游戏
    有工具栏, 用frame来实现, 目前只包含好友列表功能(支持修改)
    窗口应该包含创建聊天室和连接好友功能. 还可以一键查找上线好友
    '''
    def __init__(self, username, friendList, file):
        super().__init__()
        self.isInChatroom = False
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.__username = username
        self.__friendList = friendList
        self.__file = file
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self)

        gameMenu = tk.Menu(menubar, tearoff=0)
        gameMenu.add_command(label='Janken', command=self.game_janken)
        # filemenu.add_separator()  #这样可以用线隔开
        menubar.add_cascade(label='Game', menu=gameMenu)

        settingsMenu = tk.Menu(menubar, tearoff=0)
        settingsMenu.add_command(label='Settings')
        menubar.add_cascade(label='Settings', menu=settingsMenu)

        helpMenu = tk.Menu(menubar, tearoff=0)
        helpMenu.add_command(label='How to use', command=self.how_to_use)
        helpMenu.add_command(label='About ConnectAndPlay', command=self.about_connectAndPlay)
        menubar.add_cascade(label='Help', menu=helpMenu)

        self.config(menu=menubar)

        toolbar = tk.Frame(self)
        friendListButton = tk.Button(toolbar, text='Friend List', command=self.friend_list)
        friendListButton.pack()
        toolbar.pack()

        waitButton = tk.Button(self, text='Wait for somebody', command=self.start_server)
        waitButton.pack()
        connectButton = tk.Button(self, text='Connect somebody', command=self.connect_somebody)
        connectButton.pack()

    def start_server(self):
        if self.isInChatroom:
            messagebox.showwarning('Warning', 'Currently you can only have one chatroom')
            return
        # TODO: 改变了PORT客户端就无法连接, 需要解决
        # for i in range(10):
        #     try:
        #         serverToplevel = ServerGUI(self, '', settings.PORT + i)
        #         self.isInChatroom = True
        #         serverToplevel.title('Chatroom - server')
        #     except OSError:
        #         if i == 10:
        #             raise OSError
        #         continue
        #     break

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.3)
            sock.bind(('', settings.PORT))
            sock.listen(5)
            self.serverToplevel = ServerGUI(self, sock)
            self.isInChatroom = True
            self.serverToplevel.title('Chatroom - server')
        except:
            messagebox.showwarning('Warning', 'Cannot start a server. %d may be occupied.' % settings.PORT)


    def connect_somebody(self):
        if self.isInChatroom:
            messagebox.showwarning('Warning', 'Currently you can only have one chatroom')
            return
        chooseServerToplevel = ChooseServerToplevel(self)
        chooseServerToplevel.title('Build connection')

    def friend_list(self):
        friendListToplevel = FriendListToplevel(self)
        friendListToplevel.title('Friend List')

    def get_username(self):
        return self.__username

    def set_username(self, username):
        self.__username = username

    def get_friendList(self):
        return self.__friendList.copy()

    def update_friendList(self, friendList):
        self.__friendList = friendList
        open(self.__file.name, 'w').write(json.dumps([self.__username, self.__friendList]))

    def add_to_friendList(self, herUsername, ip):
        self.__friendList[ip] = herUsername

    def about_connectAndPlay(self):
        aboutToplevel = tk.Toplevel(self)
        aboutToplevel.title('About ConnectAndPlay')
        aboutText = tk.Text(aboutToplevel)
        aboutText.insert(tk.END, 'Version: %s\n' % settings.VERSION_NUMBER)
        aboutText.insert(tk.END, 'Author: %s\n' % settings.AUTHOR)
        aboutText.config(state='disabled')
        aboutText.pack()

    def how_to_use(self):
        howToplevel = tk.Toplevel(self)
        howToplevel.title('How to use')
        howText = tk.Text(howToplevel)
        howText.insert(tk.END, 'Call handsome Zijin Shi and you will know how to use me')
        howText.config(state='disabled')
        howText.pack()

    def game_janken(self):
        pass

    def quit(self):
        try:
            self.clientToplevel.quit()
        except:
            pass
        try:
            self.serverToplevel.quit()
        except:
            pass
        self.destroy()




class ChooseServerToplevel(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        self.hintLabel = tk.Label(self, text='Enter ip or nickname and click "Connect"')
        self.hintLabel.pack()
        self.serverInput = tk.Entry(self)
        self.serverInput.pack()
        self.connectButton = tk.Button(self, text='Connect', command=self.connect_to)
        self.connectButton.pack()

    def connect_to(self):
        serverStr = self.serverInput.get()
        self.serverInput.delete(0,tk.END)
        if serverStr == '':
            return

        correspondIp = serverStr
        for ip, nickname in self.master.get_friendList().items():
            if nickname == serverStr:
                correspondIp = ip
                break

        addr = (correspondIp, settings.PORT)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            sock.connect(addr)
            self.master.clientToplevel = ClientGUI(self.master, sock, addr)
            self.master.isInChatroom = True
            self.master.clientToplevel.title('Chatroom - client')
        except:
            messagebox.showwarning('Warning', 'Cannot connect to %s' % serverStr)
        finally:
            self.destroy()


class FriendListToplevel(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.friendList = master.get_friendList()
        self.addButton = tk.Button(self, text='Add Friend', command=self.add_friend)
        self.addButton.pack()
        self.saveButton = tk.Button(self, text='Confirm', command=self.save_modification)
        self.saveButton.pack()
        self.table = tk.Frame(self)
        self.refresh_table()

    def refresh_table(self):
        self.table.destroy()
        self.table = tk.Frame(self)
        rowNum = 0
        for ip, nickname in sorted(self.friendList.items()):
            tk.Label(self.table, text='%s' % nickname).grid(row=rowNum, column=0, sticky='W')
            tk.Label(self.table, text='%s' % ip).grid(row=rowNum, column=1, sticky='W')
            # ipLabel[rowNum].grid(row=rowNum, column=1)
            tk.Button(self.table, text='Delete', command=partial(self.delete_friend, ip)).grid(row=rowNum, column=2)
            rowNum += 1
        self.table.pack()


    def delete_friend(self, ip):
        del self.friendList[ip]
        self.refresh_table()

    def save_modification(self):
        self.master.update_friendList(self.friendList)
        self.destroy()

    def add_friend(self):
        addFriendToplevel = tk.Toplevel(self)
        addFriendToplevel.title('Add Friend')
        nicknameLabel = tk.Label(addFriendToplevel, text='Nickname')
        nicknameLabel.grid(row=0, column=0)
        ipLabel = tk.Label(addFriendToplevel, text='Ip')
        ipLabel.grid(row=1, column=0)
        nicknameEntry = tk.Entry(addFriendToplevel)
        nicknameEntry.grid(row=0, column=1)
        ipEntry = tk.Entry(addFriendToplevel)
        ipEntry.grid(row=1, column=1)
        def add_friend_confirm():
            ip = ipEntry.get()
            if ip == '':
                messagebox.showwarning('Warning', 'Please enter ip address')
                return
            nickname = nicknameEntry.get()
            if nickname == '':
                messagebox.showwarning('Warning', 'Please enter nickname')
                return
            if not self.add_friend_check(nickname, ip):
                return
            addFriendToplevel.destroy()
            self.refresh_table()
        addButton = tk.Button(addFriendToplevel, text='Add', command=add_friend_confirm)
        addButton.grid(row=2, column=1)

    def add_friend_check(self, nickname, ip):
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            messagebox.showwarning('Warning', 'Invalid IPv4 format')
            return False
        if nickname in self.friendList.values():
            messagebox.showwarning('Warning', 'Nicknames cannot repeat!')
            return False
        if ip in self.friendList:
            if nickname == self.friendList[ip]:
                return True
            answer = messagebox.askquestion('Confirm', 'IP already exists. Do you want to change the nickname from \"%s\" to \"%s\"?'
                                            % (self.friendList[ip], nickname), icon='info')
            if answer == 'yes':
                self.friendList[ip] = nickname
                return True
            else:
                return False

        self.friendList[ip] = nickname
        return True

        # if (ip in self.friendList) and (self.friendList[ip] != None):
        #     if (nickname == self.friendList[ip]) or (nickname == None):
        #         return
        #     answer = messagebox.askquestion('Warning', 'IP already exists. Do you want to change the nickname from \"%s\" to \"%s\"?'
        #                                     % (self.friendList[ip], nickname), icon='warning')
        #     if answer == 'yes':
        #         if nickname in self.friendList.values():
        #             messagebox.showinfo('Warning', 'Warning: nicknames repeated', icon='warning')
        #         self.friendList[ip] = nickname
        #     else:
        #         return
        # else:
        #     if (nickname in self.friendList.values()) and (nickname != None):
        #         messagebox.showinfo('Warning', 'Warning: nicknames repeated', icon='warning')
        #     self.friendList[ip] = nickname
