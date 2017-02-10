from queue import Queue
from enum import Enum
import logging
import json
import os

logging.basicConfig(level=logging.ERROR)

VERSION_NUMBER = 0.4
AUTHOR = 'Zijin Shi'

PORT = 8800

class Mode(Enum):
    CLOSE = 0
    NORMAL = 1
    SERVER = 2
    CLIENT = 3
    GAME = 4

def get_addr_name(addr):
    ip = addr[0]
    if ip in friendList:
        return friendList[ip]
    else:
        return ip

def get_connect_thread(ip=None):
    if mode == Mode.SERVER:
        return tServer.get_slave_thread(ip)
    elif mode == Mode.CLIENT:
        assert ip == None, 'Redundant parameters'
        return tClient
    else:
        return None

commandsForProcess = Queue()
tServer = None
tClient = None
mode = Mode.NORMAL
gameThread = None

filePath = os.path.join(os.path.abspath('.'), 'FriendList.txt')

# TODO: 此处我感觉好像没有问题, 但是有机会最好检查一下
try:
    with open(filePath, 'r') as file:
        jsonStr = file.read()
    savedData = json.loads(jsonStr)
    username = savedData[0]
    friendList = savedData[1]
except (IOError, json.decoder.JSONDecodeError):
    print('This is the first time you use ConnectAndPlay or your saved data is lost.')
    username = input('Please enter your username. You can change it later: ')
    friendList = {}
    with open(filePath, 'w') as newFile:
        newFile.write(json.dumps([username, {}]))

