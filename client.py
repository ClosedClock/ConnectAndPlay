import socket

import settings
from settings import Mode, logging
from connect_thread import ConnectThread

class ClientThread(ConnectThread):
    def __init__(self, addr):
        logging.info('Initializing a ServerThread object')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        sock.connect(addr)
        super().__init__(sock, addr)
        logging.info('A ServerThread object created')

    def run(self):
        print('Connected to %s' % self.get_nickname())
        super().run()
        settings.mode = Mode.NORMAL
        print('Connection to %s closed.' % self.get_nickname())

    def quit(self):
        logging.info('Set the ClientThread isRunning flag to False')
        super().quit()


