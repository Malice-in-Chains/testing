# -*- coding: utf-8 -*-

import os
import random
import logging

from time import time
from hashlib import md5
from base64 import b64encode, b64decode
from models import dbsession, User, Dictionary
from libs.Form import Form
from libs.EmailService import EmailService
from libs.SecurityDecorators import async
from handlers.BaseHandlers import BaseHandler


class HomePageHandler(BaseHandler):
    ''' User handlers extend this class '''
    
    def get(self, *args, **kwargs):
        self.render('public/home_page.html')


class BlogHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('public/blog.html')


class LoginHandler(BaseHandler):
    ''' User handlers extend this class '''
    
    def get(self, *args, **kwargs):
        self.render('public/login.html', errors=None)

    def post(self, *args, **kwargs):
        ''' Attempt to log into an account '''
    	form = Form(
            username="Please enter a username",
            password="Please enter a password",
        )
        if form.validate(self.request.arguments):
            user = User.by_name(self.get_argument('username'))
            if user is not None:
                if user.validate_password(self.get_argument('password')):
                    if user.confirmed:
                        self.successful_login(user)
                        if user.has_permission('administrator'):
                            self.redirect('/admin')
                        else:
                            self.redirect('/user')
                    else:
                        self.render('public/login.html', errors=["You must confirm your email address before you can login"])
                else:
                    self.render('public/login.html', errors=["Invalid password"])
            else:
                self.render('public/login.html', errors=["Invalid username"])
        else:
            self.render('public/login.html', errors=form.errors)

    def successful_login(self, user):
        ''' Successful login; create session '''
        logging.info("Successful login: %s from %s" % (user.name, self.request.remote_ip,))
        self.start_session()
        self.session['user_id'] = int(user.id)
        self.session['user_name'] = ''.join(user.name) # Copy string
        home_dir = self.application.settings['user_files'] + '/%s/' % (user.uuid,)
        hmac = md5()
        hmac_secret = os.urandom(8).encode('hex')
        hmac.update(home_dir + hmac_secret)
        self.session['hmac_secret'] = hmac_secret
        self.set_cookie('home', "%s|%s" % (b64encode(home_dir), hmac.hexdigest()))
        if user.has_permission('administrator'):
            self.session['menu'] = 'admin'
        else:
            self.session['menu'] = 'user'
        self.session.save()


class RegistrationHandler(BaseHandler):
    ''' User handlers extend this class '''
    
    def get(self, *args, **kwargs):
        self.render('public/registration.html', errors=None)

    def post(self, *args, **kwargs):
    	''' Create  a new user '''
        form = Form(
            username="Please enter a username",
            email="Please enter a valid email address",
            password1="Please enter a password",
            password2="Please confirm your password",
        )
        if form.validate(self.request.arguments):
            if User.by_name(self.get_argument('username')) is not None:
                error_msg = "Username already taken; if you forgot your password use the password recovery option"
                self.render('public/registration.html', errors=[error_msg])
            elif User.by_email(self.get_argument('email')) is not None:
                error_msg = "Email already in use; if you forgot your password use the password recovery option"
                self.render('public/registration.html', errors=[error_msg])
            elif self.get_argument('password1') != self.get_argument('password2'):
                self.render('public/registration.html', errors=["Passwords do not match"])
            else:
                email_service = EmailService()
                user = self.create_user(self.get_argument('username'), self.get_argument('email'), self.get_argument('password1'))
                email_service.send_confirmation(user)
                self.render('public/registration_successful.html', user=user)
        else:
            self.render('public/registration.html', errors=form.errors)

    def create_user(self, username, email, password):
    	''' Add user to database '''
        user = User(
            name=unicode(username),
            email=unicode(email),
        )
        dbsession.add(user)
        user.password = password
        dbsession.add(user)
        dbsession.flush()
        return user


class PasswordRecoveryHandler(BaseHandler):
    ''' Email user a new password '''

    def get(self, *args, **kwargs):
        self.render('public/password_recovery.html', errors=None)

    def post(self, *args, **kwargs):
        ''' Starts the account recovery proccess '''
        username = self.get_argument('username', '__NONE__')
        user = User.by_name(username)
        if user is not None and user.confirmed:
            self.reset_password(user)
            self.render('public/sent_password_recovery.html', user=user)
        else:
            self.render('public/password_recovery.html', errors=["Invalid username"])

    @async
    def reset_password(self, user):
        ''' Generate secure password, and email to user '''
        random.seed(int(time()))
        count = Dictionary.word_count()
        index = random.randint(0, count)
        word = Dictionary.at(index)
        new_password = "%s%04d" % (word, random.randint(0, 9999),)
        user.password = new_password
        dbsession.add(user)
        dbsession.flush()
        email_service = EmailService()
        email_service.send_password_recovery(user, new_password)


class ConfirmEmailHandler(BaseHandler):

    def get(self, *args, **kwargs):
    	''' Confirm user email address '''
        uuid = self.get_argument('uuid', '__NONE__')
        user = User.by_uuid(uuid)
        if user is not None and not user.confirmed:
            user.confirmed = True
            dbsession.add(user)
            dbsession.flush()
            user_dir = self.application.settings['user_files'] + '/%s/' % (user.uuid,)
            os.mkdir(os.path.abspath(user_dir))
            self.render('public/confirmed_email.html', user=user)
        else:
            self.render('public/invalid_uuid.html')


class LogoutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Clears cookies and session data '''
        if self.session != None:
            self.session.delete()
        self.clear_all_cookies()
        self.redirect("/")

class RobotsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders a fake robots.txt file to screw with people/bots '''
        self.set_header('Content-Type', 'text/plain')
        self.write("# Disallow spiders for extra security\n")
        self.write("User-agent: *\n")
        self.write("Disallow: /admin\n")
        self.finish()