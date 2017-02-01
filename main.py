

from deal_command import CommandList
import settings
from settings import Mode, logging


def deal_commands():
    while settings.mode != Mode.CLOSE:
        newCommand = settings.commandsForProcess.get(True)
        logging.info('Got a new command: %s' % newCommand)
        try:
            logging.info('Try to execute command: %s' % newCommand)
            CommandList.run(newCommand)
            #print('newCommand is:' + newCommand)
            logging.info('Finished executing command: %s' % newCommand)
        except Exception as e:
            print(e)
            print('Unknown command! Input \"help\" to list all commands.')
    logging.info('Cycle finshed')


def main():
    print('ConnectAndPlay (author @%s) v%s started' % (settings.AUTHOR, settings.VERSION_NUMBER))

    # tDealCommands = threading.Thread(target=deal_commands, args=())
    # tDealCommands.start()
    #
    # while settings.mode != Mode.CLOSE:
    #     if not settings.commandsForProcess.empty():
    #         sleep(0.1)
    #         continue
    #
    #     if settings.mode == Mode.NORMAL:
    #         print('>>> ', end='')
    #     # elif settings.mode == Mode.SERVER or settings.mode == Mode.CLIENT:
    #     #     print('%s:> ' % settings.username, end='')
    #
    #     newCommand = input()
    #     settings.commandsForProcess.put(newCommand)
    #
    # logging.info('Main thread is waiting for join()')
    # tDealCommands.join()
    # logging.info('Main thread closed')

    while settings.mode != Mode.CLOSE:
        if settings.mode == Mode.NORMAL:
            print('>>> ', end='')
        newCommand = input()
        logging.info('Got a new command: %s' % newCommand)
        try:
            logging.info('Try to execute command: %s' % newCommand)
            CommandList.run(newCommand)
            #print('newCommand is:' + newCommand)
            logging.info('Finished executing command: %s' % newCommand)
        except Exception as e:
            print(e)
            print('Unknown command! Input \"help\" to list all commands.')

    logging.info('Main thread closed')



if __name__ == '__main__':
    main()