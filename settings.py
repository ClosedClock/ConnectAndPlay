import logging

from janken import Janken
logging.basicConfig(level=logging.INFO)

VERSION_NUMBER = 0.4
AUTHOR = 'Zijin Shi'
PORT = 8800


class GameSettings(object):
    def __init__(self, name, function, type, maxRounds, hasAI):
        self.name = name
        self.function = function
        self.type = type
        self.maxRounds = maxRounds
        self.hasAI = hasAI


gameDict = {
    'Janken': GameSettings('Janken', Janken, 'Turn-Based', 10, False),
    'Gomoku': GameSettings('Gomoku', None, 'Turn-Based', 1, False)
}