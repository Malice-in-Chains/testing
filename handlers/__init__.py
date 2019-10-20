# -*- coding: utf-8 -*-


import os
import logging
import tornado.web

from tornado.web import Application
from tornado.web import StaticFileHandler 
from os import urandom, path
from base64 import b64encode
from libs.ConfigManager import ConfigManager
from modules.Menu import Menu
from handlers.PublicHandlers import *
from handlers.ErrorHandlers import *
from handlers.UserHandlers import *
from handlers.AdminHandlers import *


config = ConfigManager.Instance()
application = Application([

        #Static Handlers - Serves static CSS, JavaScript and image files
        (r'/static/(.*)', StaticFileHandler, {'path': 'static/'}),
        
        # Public Handlers
        (r'/', HomePageHandler),
        (r'/blog', BlogHandler),
        (r'/home', HomePageHandler),
        (r'/login', LoginHandler),
        (r'/registration', RegistrationHandler),
        (r'/recovery', PasswordRecoveryHandler),
        (r'/confirm_email(.*)', ConfirmEmailHandler),
        (r'/logout', LogoutHandler),
        (r'/robot(s|s.txt)', RobotsHandler),

        # User Handlers 
        (r'/user', AccountSummaryHandler),
        (r'/upload', FileUploadHandler),
        (r'/download(.*)', FileDownloadHandler),
        (r'/delete(.*)', FileDeleteHandler),
        (r'/settings', SettingsHandler),

        # Admin Handlers
        (r'/admin(.*)', CmsHandler),

        # Error Handlers
        (r'/403', UnauthorizedHandler),
      	(r'/(.*)', NotFoundHandler),
    ],

    # Template directory
    template_path='templates/',

    # Randomly generated secret key
    cookie_secret=urandom(64).encode('hex'),
    
    # UI Modules
    ui_modules={
        "Menu": Menu, 
    },

    # Save files to
    user_files=os.path.abspath('files/'),

    # Unauthorized redirects to
    login_url='/login',
    forbidden_url='/403',

    # Debug mode
    debug=True,
    
    # Application version
    version='0.0.1'
)

# Main entry point
def start_server():
     try:
          application.listen(config.listen_port)
          tornado.ioloop.IOLoop.instance().start()
     except KeyboardInterrupt:
          print "\r[!] Shutting Down!"
