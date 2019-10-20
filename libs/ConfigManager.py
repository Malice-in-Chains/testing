# -*- coding: utf-8 -*-
'''
Created on June 30, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


import os
import sys
import getpass
import logging
import ConfigParser

from libs.ConsoleColors import *
from libs.Singleton import Singleton


# .basicConfig must be called prior to ANY call to logging.XXXX so make sure
# this module gets imported prior to any logging!
#logging.basicConfig(format='\r[%(levelname)s] %(asctime)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger()
hdlr = logging.FileHandler('/var/log/cloudbox.log')
formatter = logging.Formatter('\r[%(levelname)s] %(asctime)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

@Singleton
class ConfigManager(object):
    '''  Central class which handles any user-controlled settings '''

    def __init__(self, cfg_file='cloudbox.cfg'):
        self.cfg_path = os.path.abspath(cfg_file)
        if not (os.path.exists(self.cfg_path) and os.path.isfile(self.cfg_path)):
            logging.critical("No configuration file found at %s, cannot continue." %
                             self.cfg_path)
            os._exit(1)
        logging.info('Loading config from %s' % self.cfg_path)
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(self.cfg_path, 'r'))
        self.__server__()
        self.__database__()
        self.__email__()
        self.__sessions__()

    def __email__(self):
        self.email_username = self.config.get("Email", 'username')
        self.email_password = self.config.get("Email", 'password')

    def __server__(self):
        ''' Load network configurations '''
        self.listen_port = self.config.getint("Server", 'port')
        log_level = self.config.get("Server", 'logging')
        logger = logging.getLogger()
        if log_level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif log_level.lower() == 'info':
            logger.setLevel(logging.INFO)
        elif log_level.lower() == 'warn':
            logger.setLevel(logging.WARN)
        else:
            sys.stdout.write(WARN + "Logging level has not been set.\n")
            logger.setLevel(logging.NOTSET)
        sys.stdout.flush()
        self.debug = self.config.getboolean("Server", 'debug')
        self.domain = self.config.get("Server", 'domain')

    def __sessions__(self):
        ''' Session settings '''
        self.memcached_server = self.config.get("Sessions", 'memcached')
        self.session_age = self.config.getint("Sessions", 'session_age')
        self.session_regeneration_interval = self.config.getint(
            "Sessions", 'session_regeneration_interval')

    def __database__(self):
        ''' Loads database connection information '''
        self.db_server = self.config.get("Database", 'db_server', "localhost")
        self.db_name = self.config.get("Database", 'db_name', "rootthebox")
        user = self.config.get("Database", 'db_user', "RUNTIME")
        if user == 'RUNTIME':
            user = raw_input(PROMPT + "Database User: ")
        self.db_user = user
        password = self.config.get("Database", 'db_password', "RUNTIME")
        if password == 'RUNTIME':
            sys.stdout.write(PROMPT + "Database ")
            sys.stdout.flush()
            password = getpass.getpass()
        self.db_password = password
