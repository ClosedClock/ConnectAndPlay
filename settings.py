from queue import Queue
from enum import Enum
#import threading

VERSION_NUMBER = 0.1
AUTHOR = 'Zijin Shi'

class Mode(Enum):
    NORMAL = 0
    SERVER = 1
    CLIENT = 2



commandsForProcess = Queue()
connectedSocks = []
connectedServer = None
name = 'Zijin'
mode = Mode.NORMAL