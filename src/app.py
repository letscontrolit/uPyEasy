#          
# Filename: app.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : App core functions and init
# Usage   : Initialize the core app functions
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import picoweb
from utemplate import source

ROUTES = [
    # You can specify exact URI string matches...
#    ("/favicon.ico", lambda req, resp: (yield from app.sendfile(resp, "/static/favicon.ico"))),
]

class EasyApp(picoweb.WebApp):

    def init(self):
        super().init()

app = EasyApp(__name__, ROUTES)
# Add our own templates to the template path
app.template_loader = source.Loader(app.pkg, "templates")