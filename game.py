
import settings
from settings import Mode

class Game(object):
    def __init__(self, connectThread):
        self.__thread = connectThread
        self.__nickname = connectThread.get_nickname()