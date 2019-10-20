# -*- coding: utf-8 -*-


import os

from string import ascii_letters, digits
from handlers.BaseHandlers import BaseHandler
from models import dbsession
from models.BlogEntry import BlogEntry
from libs.SecurityDecorators import *

class CmsHandler(BaseHandler):

    @authorized('administrator')
    def get(self, *args, **kwargs):
        self.render('admin/blog_manager.html', errors=None)

    @authorized('administrator')
    def post(self, *args, **kwargs):
        ''' Update static content '''
        print 'keys:', self.request.files.keys()
        title = self.get_argument('title', None)
        paragraph = self.get_argument('paragraph', None)
        if paragraph is None:
            self.render('admin/blog_manager.html', errors=["No text to post, write a paragraph or two!"])
        elif title is None or 64 < len(title):
        	self.render('admin/blog_manager.html', errors=["You must provide a valid title"])
        elif self.request.files.has_key('upload') and len(self.request.files['upload'][0]['filename']) == 0:
            self.render('admin/blog_manager.html', errors=["You must provide an image file"])
        else:
            file_name = os.path.basename(self.request.files['upload'][0]['filename'])
            char_white_list = ascii_letters + digits + "-._"
            file_name = filter(lambda char: char in char_white_list, file_name)
            file_path = 'static/images/%s' % (file_name,)
            f = open(file_path, 'wb')
            f.write(self.request.files['upload'][0]['body'])
            f.close()
            self.create_blog_entry(title, paragraph, file_name)
            self.redirect('/blog')

    def create_blog_entry(self, title, paragraph, pic_name):
        entry = BlogEntry(
        	title=unicode(title),
            paragraph=unicode(paragraph),
            image_uri=unicode('/static/images/'+pic_name),
        )
        dbsession.add(entry)
        dbsession.flush()

