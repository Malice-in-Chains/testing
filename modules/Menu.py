# -*- coding: utf-8 -*-
'''
Created on Mar 14, 2012

@author: moloch

    Copyright 2012 Root the Box

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


from tornado.web import UIModule
from models import User


class Menu(UIModule):

    def render(self, *args, **kwargs):
        ''' Renders the top menu '''
        if self.handler.session != None:
            user = User.by_id(self.handler.session['user_id'])
            if self.handler.session['menu'] == 'user':
                return self.render_string('menu/user.html', user=user)
            elif self.handler.session['menu'] == 'admin':
                return self.render_string('menu/admin.html', user=user)
        return self.render_string('menu/public.html')
