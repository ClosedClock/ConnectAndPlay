#from multiprocessing import Process
import threading
#from queue import Queue
from time import sleep

from deal_command import *
import settings


def dealCommands():
    while True:
        newCommand = settings.commandsForProcess.get(True)
        if (newCommand == 'exit' and settings.mode == Mode.NORMAL) or (newCommand == '\\exit' and settings.mode != Mode.NORMAL):
            break
        try:
            CommandList.run(newCommand)
            #print('newCommand is:' + newCommand)
        except Exception as e:
            print(e)
            print('Unknown command! Input \"help\" to list all commands.')


def main():
    print('ConnectAndPlay (author @%s) v%s started' % (settings.AUTHOR, VERSION_NUMBER))

    tDealCommands = threading.Thread(target=dealCommands, args=())
    tDealCommands.start()

    while True:
        if not settings.commandsForProcess.empty():
            sleep(0.1)
            continue

        if settings.mode == Mode.NORMAL:
            print('>>> ', end='')
        elif settings.mode == Mode.SERVER:
            print('%s:> ' % name)

        newCommand = input()
        settings.commandsForProcess.put(newCommand)
        if (newCommand == 'exit' and settings.mode == Mode.NORMAL) or (newCommand == '\\exit' and settings.mode != Mode.NORMAL):
            break

    tDealCommands.join()

if __name__ == '__main__':
    main()