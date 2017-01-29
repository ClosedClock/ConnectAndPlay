import re

from server import start_server
from client import connect_to
import settings
from settings import Mode, logging

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
        for k, v in CommandList.commandDict.items():
            print('%s:    %s' % (k, v[2]))
    elif commandName in CommandList.commandDict:
        print('%s: %s' % (commandName, CommandList.commandDict[commandName][2]))
    else:
        raise KeyError('Command not found.')


def shut_down_server():
    logging.info('Current connected socks:')
    for sockName in settings.tServer.get_connected_socks().keys():
        logging.info('%s:%s' % sockName)
    if settings.mode != Mode.SERVER:
        print('You are not in SERVER mode.')
        return
    settings.mode = Mode.NORMAL
    settings.tServer.close()
    logging.info('All socks closed')

def stop_connection():
    logging.info('Current connected server: %s:%s' % settings.tClient.get_connected_server())
    if settings.mode != Mode.CLIENT:
        print('You are not in CLIENT mode.')
        return
    settings.mode = Mode.NORMAL
    settings.tClient.quit()
    logging.info('Connection closed')




def list_friend():
    pass

def add_friend():
    pass

def delete_friend():
    pass


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
        'waiting':      [start_server, 0,
                        'During waiting, if someone connects you, than you can begin to play!'],
        'exit':         [exit, 0,
                        'Terminate the program.']
    }

    connectedCommandDict = {
        'close':         [shut_down_server, 0,
                         'Shut down the server.'],
        'quit':          [stop_connection, 0,
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
                logging.info('This is a command in SERVER mode: %s' % command)
                commandWords = re.split(r'\s+', command[1:])
                CommandList.connectedCommandDict[commandWords[0]][0](*commandWords[1:])
            else:
                print(command)
                settings.tServer.say(command)
        elif settings.mode == Mode.CLIENT:
            if command[0] == '\\':
                commandWords = re.split(r'\s+', command[1:])
                CommandList.connectedCommandDict[commandWords[0]][0](*commandWords[1:])
            else:
                print(command)
                settings.tClient.say(command)
        else:
            return


