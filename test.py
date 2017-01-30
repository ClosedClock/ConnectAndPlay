from enum import Enum


class JankenGesture(Enum):
    ROCK = 0
    SCISSORS = 1
    PAPER = 2


a = JankenGesture(0)
print(a == JankenGesture.ROCK)
