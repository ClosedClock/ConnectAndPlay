import re

from server import *
from client import *
import settings


def guide(commandName = ''):
    if commandName == '':
        print('Here lists all available commands.')
        for k, v in CommandList.commandDict.items():
            print('%s:    %s' % (k, v[2]))
    elif commandName in CommandList.commandDict:
        print('%s: %s' % (commandName, CommandList.commandDict[commandName][2]))
    else:
        raise KeyError('Command not found.')


def shutDownServer():
    if settings.mode == Mode.NORMAL:
        print('You are not connection to anyone.')
        return
    settings.mode = Mode.NORMAL
    for sock in settings.connectedSocks:
        sock.close()
    settings.connectedSocks = []

def stopConnection():
    pass




def listFriend():
    pass

def addFriend():
    pass

def deleteFriend():
    pass


class CommandList(object):
    commandDict = {
        '?':            [guide, 0,
                        'Show help information.'],
        'help':         [guide, 0,
                        'Show help information.'],
        'friendlist':   [listFriend, 0,
                        'Show friends list and their ips.'],
        'addfriend':    [addFriend, 0,
                        'Add a new friend and his/her ip to the list.'],
        'deletefriend': [deleteFriend, 0,
                        'Delete a friend from the list.'],
        'connect':      [connectTo, 0,
                        'Connect to a friend\'s computer. Only works if that friend is acting as a server.'],
        'waiting':      [startServer, 0,
                        'During waiting, if someone connects you, than you can begin to play!'],
        'exit':         [None, 0,
                        'Terminate the program.']
    }

    connectedCommandDict = {
        'close':         [shutDownServer, 0,
                         'Shut down the server.'],
        'quit':          [stopConnection, 0,
                         'Stop the connetion.']
    }
    connectedCommandDict.update(commandDict)

    @staticmethod
    def run(command):
        if settings.mode == Mode.NORMAL:
            commandWords = re.split(r'\s+', command)
            CommandList.commandDict[commandWords[0]][0](*commandWords[1:])
        elif settings.mode == Mode.SERVER:
            if command[0] == '\\':
                commandWords = re.split(r'\s+', command[1:])
                CommandList.commandDict[commandWords[0]][0](*commandWords[1:])
            else:
                print(command)
                for sock in connectedSocks:
                    sock.send(command.encode('utf-8'))
        elif settings.mode == Mode.CLIENT:
            if command[0] == '\\':
                commandWords = re.split(r'\s+', command[1:])
                CommandList.commandDict[commandWords[0]][0](*commandWords[1:])
            else:
                print(command)
                connectedServer.send(command.encode('utf-8'))


