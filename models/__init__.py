# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Integer
from sqlalchemy.orm import sessionmaker
from models.BaseObject import BaseObject

metadata = BaseObject.metadata

# set the connection string here
engine = create_engine('mysql://cloudbox:cloudbox@localhost/CloudBox')
Session = sessionmaker(bind=engine, autocommit=True)

# import the dbsession instance to execute queries on your database
dbsession = Session(autoflush=True)

# import models.
from models.User import User
from models.Dictionary import Dictionary
from models.Permission import Permission
from models.BlogEntry import BlogEntry

# calling this will create the tables at the database
create_tables = lambda: (setattr(engine, 'echo', True), metadata.create_all(engine))

# Bootstrap the database with some shit
def boot_strap():
    import setup.bootstrap
