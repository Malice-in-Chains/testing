# -*- coding: utf-8 -*-


import os
import pickle
import logging
import traceback

from string import ascii_letters, digits
from base64 import b64encode, b64decode
from mimetypes import guess_type
from libs.Form import Form
from libs.SecurityDecorators import *
from hashlib import md5
from handlers.BaseHandlers import BaseHandler
from models import dbsession


class SavedFile(object):

    def __init__(self, owner, content_type, data):
        self.owner = owner
        self.content_type = content_type
        self.data = b64encode(data)

    def get_contents(self):
        return b64decode(self.data)

    def __len__(self):
        return len(self.get_contents())


class AccountSummaryHandler(BaseHandler):
    
    @authenticated
    def get(self, *args, **kwargs):
        try:
            home = self.get_hmac_cookie('home')
            self.render('user/summary.html', errors=None, dir=home)
        except ValueError:
            stacktrace = traceback.format_exc()
            self.write_error("Cookie HMAC failed to authenticate; logout and then login again to fix this issue", stacktrace)
            self.finish()
        except:
            stacktrace = traceback.format_exc()
            self.write_error("ERROR (?): Unknown error, try again later", stacktrace)
            self.finish()
    
    def get_hmac_cookie(self, cookie_name):
        ''' Verifies cookie has not been tampered with HMAC '''
        cookie = self.get_cookie(cookie_name).split('|')
        if len(cookie) != 2:
            raise IndexError("Malformed cookie string; must be b64(value)|hmac")
        hmac = md5()
        hmac.update(b64decode(cookie[0]) + self.session['hmac_secret'])
        if hmac.hexdigest() != cookie[1]:
            raise ValueError("Invalid HMAC md5(%s + %s) != %s" % (b64decode(cookie[0]), self.session['hmac_secret'], cookie[1]))
        else:
            return b64decode(cookie[0])

    def write_error(self, message, stacktrace=""):
        self.write("<html>\n")
        self.write("<h1>%s</h1>\n" % message)
        self.write("\n<!--\n %s \n-->\n" % str(stacktrace))
        self.write("</html>")

class FileUploadHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render('user/file_upload.html', errors=None)
    
    @authenticated
    def post(self, *args, **kwargs):
        ''' Save a user's  file '''
        try:
            user = self.get_current_user()
            file_name = os.path.basename(self.request.files['upload'][0]['filename'])
            char_white_list = ascii_letters + digits + "-._"
            file_name = filter(lambda char: char in char_white_list, file_name)
            file_path = self.application.settings['user_files'] + '/%s/%s' % (user.uuid, file_name,)
            saved_file = SavedFile(
                owner=self.get_current_user().name,
                content_type=guess_type(file_name)[0],
                data=self.request.files['upload'][0]['body'],
            )
            f = open(file_path, 'w')
            pickle.dump(saved_file, f)
            f.close()
            self.redirect('/user')
        except:
            stacktrace = traceback.format_exc()
            self.write_error("ERROR: Failed to save file.", stacktrace)

    def write_error(self, message, stacktrace=""):
        self.write("<html>\n")
        self.write("<h1>%s</h1>\n" % message)
        self.write("\n<!--\n %s \n-->\n" % str(stacktrace))
        self.write("</html>")


class FileDownloadHandler(BaseHandler):
    ''' Download files ownd by the current user '''

    @authenticated
    def get(self, *args, **kwargs):
        file_name = self.get_argument('fn', None)
        if file_name is None:
            self.write_error("ERROR: Missing parameter")
        else:
            user = self.get_current_user()
            file_name = file_name.replace('../', '')
            try:
                file_path = self.application.settings['user_files'] + '/%s/%s' % (user.uuid, file_name,)
                f = open(file_path)
                upload = pickle.load(f)
                self.set_header('Content-Type', upload.content_type)
                self.set_header('Content-Length', len(upload))
                self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
                self.write(upload.get_contents())
                f.close()
            except:
                stacktrace = traceback.format_exc()
                self.write_error("ERROR: Cannot load file", stacktrace)
        self.finish()

    def write_error(self, message, stacktrace=""):
        self.write("<html>\n")
        self.write("<h1>%s</h1>\n" % message)
        self.write("\n<!--\n %s \n-->\n" % str(stacktrace))
        self.write("</html>")


class FileDeleteHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Delete a file from CloudBox '''
        user = self.get_current_user()
        file_name = self.get_argument('fn', None)
        try:
            if file_name is None:
                raise ValueError("Missing parameter")
            file_name = file_name.replace('../', '')
            file_path = self.application.settings['user_files'] + '/%s/%s' % (user.uuid, file_name,)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                f = open(file_path)
                upload = pickle.load(f)
                if upload.owner == user.name:
                    f.close()
                    os.unlink(file_path)
                    self.redirect('/user')
                else:
                    raise ValueError("User does not own file")
            else:
                raise ValueError("Path is not a file")
        except:
            stacktrace = traceback.format_exc()
            self.write_error("ERROR: Cannot delete file", stacktrace)

    def write_error(self, message, stacktrace=""):
        self.write("<html>\n")
        self.write("<h1>%s</h1>\n" % message)
        self.write("\n<!--\n %s \n-->\n" % str(stacktrace))
        self.write("</html>")


class SettingsHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("user/settings.html", errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        form = Form(
            new_password1="Please enter a new password",
            new_password2="Please confirm the new password",
            old_password="Please enter the old password",
        )
        if form.validate(self.request.arguments):
            user = self.get_current_user()
            if user.validate_password(self.get_argument('old_password')):
                if self.get_argument('new_password1') == self.get_argument('new_password2'):
                    user.password = self.get_argument('new_password1')
                    dbsession.add(user)
                    dbsession.flush()
                    self.redirect('/logout')
                else:
                    self.render('user/settings.html', errors=["New passwords do not match"])
            else:
                self.render('user/settings.html', errors=["Invalid password"])
        else:
            self.render("user/settings.html", errors=form.errors)