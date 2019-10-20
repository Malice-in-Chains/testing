# -*- coding: utf-8 -*-

from sqlalchemy import Column, desc
from sqlalchemy.types import Unicode
from models import dbsession
from models.BaseObject import BaseObject


class BlogEntry(BaseObject):
    ''' Permission definition '''

    title = Column(Unicode(64), nullable=False)
    paragraph = Column(Unicode(4096), nullable=False)
    image_uri = Column(Unicode(1024), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def ordered(cls):
        return dbsession.query(cls).order_by(desc(cls.created)).all()