import json, os
import tkinter as tk
from tkinter import messagebox
from application import Application

# # 没有用了
# def deal_commands():
#     while settings.mode != Mode.CLOSE:
#         newCommand = settings.commandsForProcess.get(True)
#         logging.info('Got a new command: %s' % newCommand)
#         try:
#             logging.info('Try to execute command: %s' % newCommand)
#             CommandList.run(newCommand)
#             #print('newCommand is:' + newCommand)
#             logging.info('Finished executing command: %s' % newCommand)
#         except Exception as e:
#             print(e)
#             print('Unknown command! Input \"help\" to list all commands.')
#     logging.info('Cycle finshed')
#
# # main函数已经被废弃
# def main():
#     print('ConnectAndPlay (author @%s) v%s started' % (settings.AUTHOR, settings.VERSION_NUMBER))
#
#     # tDealCommands = threading.Thread(target=deal_commands, args=())
#     # tDealCommands.start()
#     #
#     # while settings.mode != Mode.CLOSE:
#     #     if not settings.commandsForProcess.empty():
#     #         sleep(0.1)
#     #         continue
#     #
#     #     if settings.mode == Mode.NORMAL:
#     #         print('>>> ', end='')
#     #     # elif settings.mode == Mode.SERVER or settings.mode == Mode.CLIENT:
#     #     #     print('%s:> ' % settings.username, end='')
#     #
#     #     newCommand = input()
#     #     settings.commandsForProcess.put(newCommand)
#     #
#     # logging.info('Main thread is waiting for join()')
#     # tDealCommands.join()
#     # logging.info('Main thread closed')
#
#     while settings.mode != Mode.CLOSE:
#         if settings.mode == Mode.NORMAL:
#             print('>>> ', end='')
#         newCommand = input()
#         logging.info('Got a new command: %s' % newCommand)
#         try:
#             logging.info('Try to execute command: %s' % newCommand)
#             CommandList.run(newCommand)
#             #print('newCommand is:' + newCommand)
#             logging.info('Finished executing command: %s' % newCommand)
#         except Exception as e:
#             print(e)
#             print('Unknown command! Input \"help\" to list all commands.')
#
#     logging.info('Main thread closed')

class usernameInputWindow(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        notice1 = tk.Label(self, text='This is the first time you use ConnectAndPlay or your saved data is lost.')
        notice1.grid(row=0, column=0, columnspan=2, sticky='W')
        notice2 = tk.Label(self, text='Please enter your username. You can change it later')
        notice2.grid(row=1, column=0, columnspan=2, sticky='W')
        self.usernameInput = tk.Entry(self)
        self.usernameInput.grid(row=2, column=0, sticky='E')
        confirmButton = tk.Button(self, text='Confirm', command=self.confirm)
        confirmButton.grid(row=2, column=1, sticky='W')
        self.username = None

    def confirm(self):
        input = self.usernameInput.get()
        if input == '':
            return
        if input[0] == ' ' or len(input) > 20:
            messagebox.showwarning('Warning', 'Invalid format!', icon='warning')
            return
        self.username = input
        self.destroy()


def main():
    filePath = os.path.join(os.path.abspath('.'), 'FriendList.txt')

    # TODO: 此处我感觉好像没有问题, 但是有机会最好检查一下
    try:
        with open(filePath, 'r') as file:
            jsonStr = file.read()
        savedData = json.loads(jsonStr)
        username = savedData[0]
        friendList = savedData[1]
    except (IOError, json.decoder.JSONDecodeError):
        UsernameInputWindow = usernameInputWindow()
        UsernameInputWindow.title('Connect And Play!')
        UsernameInputWindow.mainloop()
        # UsernameInputWindow.withdraw()
        # UsernameInputWindow.destroy()
        username = UsernameInputWindow.username
        friendList = {}
        with open(filePath, 'w') as file:
            file.write(json.dumps([username, {}]))


    # main()
    root = Application(username, friendList, file)
    root.title('Connect And Play!')
    root.mainloop()

if __name__ == '__main__':
    main()