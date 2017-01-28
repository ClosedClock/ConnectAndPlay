#from multiprocessing import Process
import threading
#from queue import Queue
from time import sleep

from deal_command import *
from global_vars import *



def dealCommands():
    global commandsForProcess
    global mode
    while True:
        newCommand = commandsForProcess.get(True)
        if (newCommand == 'exit' and mode == Mode.NORMAL) or (newCommand == '\\exit' and mode != Mode.NORMAL):
            break
        try:
            CommandList.run(newCommand)
            #print('newCommand is:' + newCommand)
        except Exception as e:
            print(e)
            print('Unknown command! Input \"help\" to list all commands.')


def main():
    print('ConnectAndPlay (author @%s) v%s started' % (AUTHOR, VERSION_NUMBER))
    global commandsForProcess

    global mode

    tDealCommands = threading.Thread(target=dealCommands, args=())
    tDealCommands.start()

    while True:
        if not commandsForProcess.empty():
            sleep(0.1)
            continue

        if mode == Mode.NORMAL:
            print('>>> ', end='')
        elif mode == Mode.SERVER:
            print('%s:> ' % name)

        newCommand = input()
        commandsForProcess.put(newCommand)
        if (newCommand == 'exit' and mode == Mode.NORMAL) or (newCommand == '\\exit' and mode != Mode.NORMAL):
            break

    tDealCommands.join()

if __name__ == '__main__':
    main()