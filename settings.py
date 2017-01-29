from queue import Queue
from enum import Enum
#import threading
import logging
logging.basicConfig(level=logging.INFO)

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
name = 'Zijin'
serverIP = '127.0.0.1'
mode = Mode.NORMAL