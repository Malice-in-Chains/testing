'''
Created on Mar 13, 2012

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


import logging
import inspect
import functools

from threading import Thread
from models.User import User


def authenticated(method):
    ''' Checks to see if a user has been authenticated '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.session is not None:
            return method(self, *args, **kwargs)
        self.redirect(self.application.settings['login_url'])
    return wrapper


def restrict_ip_address(method):
    ''' Only allows access to ip addresses in a provided list '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip in self.application.settings['admin_ips']:
            return method(self, *args, **kwargs)
        else:
            logging.warn("Attempted unauthorized access from %s to %s" %
                         (self.request.remote_ip, self.request.uri))
            self.redirect(self.application.settings['forbidden_url'])
    return wrapper


def authorized(permission):
    ''' Checks user's permissions '''

    def func(method):

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.session is not None:
                user = User.by_id(self.session['user_id'])
                if user is not None and user.has_permission(permission):
                    return method(self, *args, **kwargs)
            logging.warn("Attempted unauthorized access from %s to %s" %
                            (self.request.remote_ip, self.request.uri))
            self.redirect(self.application.settings['forbidden_url'])
        return wrapper
    return func


def async(method):
    ''' Quick and easy async functions'''
    
    @functools.wraps(method)
    def __async__(*args, **kwargs):
        worker = Thread(target=method, args=args, kwargs=kwargs)
        worker.start()
    return __async__


def debug(method):
    ''' Logs a function call '''

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__
        logging.debug("Call to -> %s.%s()" % (class_name, method.__name__,))
        value = method(*args, **kwargs)
        logging.debug("Return from <- %s.%s()" % (class_name, method.__name__,))
        return value
    return wrapper
