import re
import json

from server import ServerThread
from client import ClientGUI
from server import ServerGUI
from janken import Janken
import settings
from settings import Mode, logging

import tkinter as tk

def exit():
    if settings.mode == Mode.SERVER:
        print(r'You should close your server first by typing "\close".')
        return
    elif settings.mode == Mode.CLIENT:
        print(r'You should shut down the connection first by typing "\quit".')
        return
    logging.info('Got an exit command')
    settings.mode = Mode.CLOSE


def guide(commandName = ''):
    if commandName == '':
        print('Here lists all available commands.')
        items = {Mode.NORMAL: CommandList.commandDict,
                 Mode.SERVER: CommandList.serverCommandDict,
                 Mode.CLIENT: CommandList.clientCommandDict
        }[settings.mode].items()
        for k, v in items:
            print('%s:    %s' % (k, v[2]))
    elif commandName in CommandList.commandDict:
        print('%s: %s' % (commandName, CommandList.commandDict[commandName][2]))
    else:
        raise KeyError('Command not found.')


def shut_down_server():
    logging.info('Current connected socks:')
    for addr in settings.tServer.get_clients_addr():
        logging.info('%s' % addr[0])
    if settings.mode != Mode.SERVER:
        print('You are not in SERVER mode.')
        return
    settings.mode = Mode.NORMAL
    settings.tServer.close()
    settings.tServer = None
    logging.info('All socks closed')


def stop_connection():
    logging.info('Current connected server: %s:%s' % settings.tClient.get_connected_addr())
    if settings.mode != Mode.CLIENT:
        print('You are not in CLIENT mode.')
        return
    settings.mode = Mode.NORMAL
    settings.tClient.quit()
    settings.tClient = None
    logging.info('Connection closed')


def save_data():
    """Save the dict friendList to the file FriendList.txt"""
    with open(settings.filePath, 'w') as file:
        file.write(json.dumps([settings.username, settings.friendList]))


def list_friend():
    if settings.friendList == {}:
        print('You don\'t have any saved friend. Add friends by \"addfriend ip (nickname)\"')
        return
    for ip, nickname in settings.friendList.items():
        if nickname == None:
            print('%s: No nickname' % ip)
        else:
            print('%s: %s' % (ip, nickname))


def add_friend(ip, nickname=None):
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        print('Invalid IPv4 format')
        return
    if (ip in settings.friendList) and (settings.friendList[ip] != None):
        if (nickname == settings.friendList[ip]) or (nickname == None):
            return
        answer = input('IP already exists. Do you want to change the nickname from \"%s\" to \"%s\"? (y/n)' % (settings.friendList[ip], nickname))
        #answer = input()
        if answer == 'y' or answer == 'Y':
            if nickname in settings.friendList.values():
                print('Warning: nicknames repeated')
            settings.friendList[ip] = nickname
            save_data()
        else:
            return
    else:
        if (nickname in settings.friendList.values()) and (nickname != None):
            print('Warning: nicknames repeated')
        settings.friendList[ip] = nickname
        save_data()


def delete_friend(str):
    if str in settings.friendList:
        del settings.friendList[str]
        save_data()
        return
    ipsOfStr = []
    for ip, nickname in settings.friendList.items():
        if nickname == str:
            ipsOfStr.append(ip)
    for ip in ipsOfStr:
        del settings.friendList[ip]
    save_data()


def start_server():
    # settings.tServer = ServerThread('', settings.PORT)
    # print('Change to SERVER mode...')
    # settings.mode = Mode.SERVER
    # settings.tServer.start()
    s = ServerGUI('', settings.PORT)
    s.mainloop()


def connect_to(str):
    if str in settings.friendList.values():
        for ip, nickname in settings.friendList.items():
            if nickname == str:
                correspondIp = ip
                break
    else:
        correspondIp = str
    # settings.tClient = ClientThread((correspondIp, settings.PORT))
    # print('Change to CLIENT mode...')
    # settings.mode = Mode.CLIENT
    # settings.tClient.start()
    c = ClientGUI((correspondIp, settings.PORT))
    c.mainloop()


def play_game(GameClass, isChallenger, *args):
    newGame = GameClass(isChallenger, *args)
    logging.info('Game started')
    newGame.play()
    newGame.game_over()
    settings.gameThread = None
    logging.info('Game finished')



class CommandList(object):
    commandDict = {
        '?':            [guide, 0,
                        'Show help information.'],
        'help':         [guide, 0,
                        'Show help information.'],
        'friendlist':   [list_friend, 0,
                        'Show friends list and their ips.'],
        'addfriend':    [add_friend, 0,
                        'Add a new friend and his/her ip to the list.'],
        'deletefriend': [delete_friend, 0,
                        'Delete a friend from the list.'],
        'connect':      [connect_to, 0,
                        'Connect to a friend\'s computer. Only works if that friend is acting as a server.'],
        'wait':      [start_server, 0,
                        'During waiting, if someone connects you, than you can begin to play!'],
        'exit':         [exit, 0,
                        'Terminate the program.']
    }

    connectCommandDict = {
        'janken':       [Janken, 1,
                         'Play the game \"Janken\" with your friend']
    }
    connectCommandDict.update(commandDict)


    serverCommandDict = {
        'close':         [shut_down_server, 0,
                         'Shut down the server.'],
    }
    serverCommandDict.update(connectCommandDict)


    clientCommandDict = {
        'quit':          [stop_connection, 0,
                         'Stop the connetion.']
    }
    clientCommandDict.update(connectCommandDict)

    @staticmethod
    def run(command):
        if re.match(r'^\s*$', command):
            return
        if settings.gameThread != None:
            logging.info('gameThread != None')
            gameCommand = settings.gameThread.get_message()
            logging.info('gameCommand: %s' % gameCommand)
            gameWords = re.split(r'\s+', gameCommand[1:])
            if command == 'y' or command == 'Y':
                logging.info('Challenge accepted')
                settings.gameThread.send_message(r'\yes')
                GameClass = CommandList.connectCommandDict[gameWords[0]][0]
                play_game(GameClass, False, *gameWords[1:])
            else:
                logging.info('Challenge refused')
                settings.gameThread.send_message(r'\no')
                settings.gameThread = None

        elif settings.mode == Mode.NORMAL:
            commandWords = re.split(r'\s+', command)
            CommandList.commandDict[commandWords[0]][0](*commandWords[1:])
        elif settings.mode == Mode.SERVER:
            if command[0] == '\\':
                logging.info('This is a command in SERVER mode: %s' % command)
                commandWords = re.split(r'\s+', command[1:])
                if commandWords[0] in CommandList.serverCommandDict:
                    value = CommandList.serverCommandDict[commandWords[0]]
                    if value[1] == 0:
                        value[0](*commandWords[1:])
                    elif value[1] == 1:
                        play_game(value[0], True, *commandWords[1:])
            else:
                logging.info('Try to say %s' % command)
                settings.tServer.say(command)
        elif settings.mode == Mode.CLIENT:
            if command[0] == '\\':
                commandWords = re.split(r'\s+', command[1:])
                if commandWords[0] in CommandList.clientCommandDict:
                    value = CommandList.clientCommandDict[commandWords[0]]
                    if value[1] == 0:
                        value[0](*commandWords[1:])
                    elif value[1] == 1:
                        play_game(value[0], True, *commandWords[1:])
            else:
                settings.tClient.send_message(command)
        else:
            return


