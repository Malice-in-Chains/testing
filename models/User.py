# -*- coding: utf-8 -*-

from base64 import b64encode
from uuid import uuid4
from hashlib import md5
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean
from string import ascii_letters, digits
from models import dbsession
from models.Permission import Permission
from models.BaseObject import BaseObject


class User(BaseObject):
    ''' 
    User class used for authentication/autorization 
    '''

    _name = Column(Unicode(64), unique=True, nullable=False)
    name = synonym('_name', descriptor=property(
        lambda self: self._name,
        lambda self, name: setattr(self, '_name', self.__class__._filter_string(name))
    ))
    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    confirmed = Column(Boolean, default=False)
    email = Column(Unicode(128), unique=True, nullable=False)
    permissions = relationship("Permission", backref=backref("User", lazy="joined"), cascade="all, delete-orphan")
    _password = Column('password', Unicode(64))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(self, '_password',
                                       self.__class__._hash_password(password))
    ))

    @classmethod
    def by_id(cls, user_id):
        ''' Return the user object whose user id is user_id '''
        return dbsession.query(cls).filter_by(id=user_id).first()

    @classmethod
    def by_uuid(cls, user_uuid):
        ''' Return the user object whose user id is user_uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(user_uuid)).first()

    @classmethod
    def all(cls):
        ''' Return all non-admin user objects '''
        return dbsession.query(cls).all()

    @classmethod
    def all_users(cls):
        ''' Return all non-admin user objects '''
        return filter(lambda user: user.has_permission('administrator') == False, cls.all())

    @classmethod
    def all_admins(cls):
        ''' Return all non-admin user objects '''
        return filter(lambda user: user.has_permission('administrator') == True, cls.all())

    @classmethod
    def by_name(cls, user_name):
        ''' Return the user object whose user name is 'user_name' '''
        return dbsession.query(cls).filter_by(name=unicode(user_name)).first()

    @classmethod
    def by_email(cls, email_address):
        ''' Return the user object whose user email is 'email_address' '''
        return dbsession.query(cls).filter_by(email=unicode(email_address)).first()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        ''' Remove any non-white listed chars from a string '''
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    @classmethod
    def _hash_password(cls, password):
        hsh = md5()
        hsh.update(password)
        return unicode(hsh.hexdigest())

    @property
    def permissions(self):
        ''' Return a list with all permissions granted to the user '''
        return dbsession.query(Permission).filter_by(user_id=self.id)

    @property
    def permissions_names(self):
        ''' Return a list with all permissions names granted to the user '''
        return [permission.name for permission in self.permissions]

    def has_permission(self, permission):
        ''' Return True if 'permission' is in permissions_names '''
        return True if permission in self.permissions_names else False

    def validate_password(self, attempt):
        ''' Check the password against existing credentials '''
        return self.password == self._hash_password(attempt)

    def __repr__(self):
        return unicode('<User - name: %s>' % (self.name,))

    def __str__(self):
        return unicode(self.name)
