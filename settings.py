from queue import Queue
from enum import Enum
import logging
import json
import os

logging.basicConfig(level=logging.ERROR)

VERSION_NUMBER = 0.1
AUTHOR = 'Zijin Shi'

PORT = 8887

class Mode(Enum):
    CLOSE = 0
    NORMAL = 1
    SERVER = 2
    CLIENT = 3



commandsForProcess = Queue()
tServer = None
tClient = None
mode = Mode.NORMAL

filePath = os.path.join(os.path.abspath('.'), 'FriendList.txt')
try:
    file = open(filePath, 'r')
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
finally:
    file.close()

