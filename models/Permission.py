# -*- coding: utf-8 -*-


from sqlalchemy.types import Unicode, Integer
from sqlalchemy import Column, ForeignKey
from models import dbsession
from models.BaseObject import BaseObject


class Permission(BaseObject):
    ''' Permission definition '''

    name = Column(Unicode(64), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    def __repr__(self):
        return u'<Permission - name: %s, user_id: %d>' % (self.name, self.user_id)

    def __unicode__(self):
        return self.name
