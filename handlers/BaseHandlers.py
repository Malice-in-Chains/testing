# -*- coding: utf-8 -*-


import logging
import pylibmc

from models import User
from libs.ConfigManager import ConfigManager
from libs.SecurityDecorators import *
from libs.Sessions import MemcachedSession
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    ''' User handlers extend this class '''

    def initialize(self):
        self.session = None
        self.config = ConfigManager.Instance()
        session_id = self.get_secure_cookie('session_id')
        if session_id is not None:
            self.conn = pylibmc.Client([self.config.memcached_server], binary=True)
            self.conn.behaviors['no_block'] = 1  # async I/O
            self.session = self._create_session(session_id)
            self.session.refresh()

    def get_current_user(self):
        ''' Get current user object from database '''
        if self.session is not None:
            try:
                return User.by_id(self.session['user_id'])
            except KeyError:
                logging.exception("Malformed session.")
                repr(self.session)
            except:
                logging.exception("Unknown error in: get_current_user()")
        return None

    def start_session(self):
        ''' Starts a new session '''
        self.conn = pylibmc.Client(
                [self.config.memcached_server], binary=True)
        self.conn.behaviors['no_block'] = 1  # async I/O
        self.session = self._create_session()
        self.set_secure_cookie(
            'session_id',
            self.session.session_id,
            expires_days=1,
            expires=self.session.expires,
            path='/',
            HttpOnly=True,
        )

    def _create_session(self, session_id=None):
        ''' Creates a new session '''
        kw = {
            'duration': self.config.session_age,
            'ip_address': self.request.remote_ip,
            'regeneration_interval': self.config.session_regeneration_interval,
        }
        new_session = None
        old_session = None
        old_session = MemcachedSession.load(session_id, self.conn)
        if old_session is None or old_session._is_expired():  # create new session
            new_session = MemcachedSession(self.conn, **kw)
        if old_session is not None:
            if old_session._should_regenerate():
                old_session.refresh(new_session_id=True)
            return old_session
        return new_session

    def get(self, *args, **kwargs):
        ''' Placeholder, incase child class does not impl this method '''
        self.render("errors/404.html")

    def post(self, *args, **kwargs):
        ''' Placeholder, incase child class does not impl this method '''
        self.render("errors/404.html")

    def put(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn("%s attempted to use PUT method" % self.request.remote_ip)
        self.render("errors/404.html")

    def delete(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use DELETE method" % self.request.remote_ip)
        self.render("errors/404.html")

    def head(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use HEAD method" % self.request.remote_ip)
        self.render("errors/404.html")

    def options(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use OPTIONS method" % self.request.remote_ip)
        self.render("errors/404.html")
