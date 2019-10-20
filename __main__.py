# -*- coding: utf-8 -*-

from os import path
from sys import argv
from time import sleep
from datetime import datetime
from libs.ConsoleColors import *


current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def serve():
    ''' Starts the application '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from handlers import start_server
    print(INFO + '%s : Starting application ... ' % current_time())
    start_server()


def create():
    ''' Creates/bootstraps the database '''
    from libs.ConfigManager import ConfigManager  # Sets up logging
    from models import create_tables, boot_strap
    print(INFO + '%s : Creating the database ... ' %
          current_time())
    create_tables()
    if len(argv) == 3 and (argv[2] == 'bootstrap' or argv[2] == '-b'):
        print('\n\n\n' + INFO + \
              '%s : Bootstrapping the database ... \n' % current_time())
        boot_strap()


### Main
if __name__ == '__main__':
    options = {
        'serve': serve,
        'start': serve,
        'create': create,
    }
    if len(argv) == 1:
        help()
    else:
        if argv[1] in options:
            options[argv[1]]()
        else:
            print(WARN + 'PEBKAC (%s): Command not found, see "python . help"' % argv[1])