'''
Created on Sep 22, 2012

@author: stormcrow

    Copyright [2012] [Redacted Labs]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import os
import smtplib
import logging
import mimetypes

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from libs.ConfigManager import ConfigManager
from libs.SecurityDecorators import async


class EmailService():

    def __init__(self):
        self.config = ConfigManager.Instance()

    @async
    def send_confirmation(self, user):
        ''' Sends the confirmation email w/link '''
        subject = 'CloudBox: Confirmation Email'
        text = 'Please follow the link below to confirm your registration\n' + \
               'http://cloudbox.rootthebox.com/confirm_email?uuid=' + user.uuid
        msg = MIMEMultipart()
        msg['From'] = self.config.email_username
        msg['To'] = user.email
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        self.__send__(msg)

    @async
    def send_password_recovery(self, user, new_password):
        ''' Sends email with recovery password '''
        logging.info("Sending recovery password to %s at %s" % (user.name, user.email,))
        subject = 'CloudBox: Password Recovery'
        text = 'Your account password has been reset to: %s\n' % new_password
        msg = MIMEMultipart()
        msg['From'] = self.config.email_username
        msg['To'] = user.email
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        self.__send__(msg)

    def __send__(self, msg):
        ''' Connects to Google SMTP server and sends email '''
        mail_server = smtplib.SMTP('smtp.gmail.com', 587)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(self.config.email_username, self.config.email_password)
        mail_server.sendmail(self.config.email_username, msg['To'], msg.as_string())
        mail_server.close()