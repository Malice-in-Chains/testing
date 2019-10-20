# -*- coding: utf-8 -*-


from sqlalchemy import Column, desc
from sqlalchemy.types import String
from models import dbsession
from models.BaseObject import BaseObject


class Dictionary(BaseObject):
    ''' Permission definition '''

    word = Column(String(32), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()
        
    @classmethod
    def word_count(cls):
        ''' Return length of the dictionary '''
        return dbsession.query(cls).order_by(desc(cls.id)).first().id

    @classmethod
    def at(cls, index):
        return dbsession.query(cls).filter_by(id=index - 1).first()

    def __str__(self):
        return self.word

    def __unicode__(self):
        return unicode(self.word)


