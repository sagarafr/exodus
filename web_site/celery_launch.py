# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import os

from web_site.foo import create_app
from web_site.foo.extensions import cel

app = create_app(
    os.getenv('APP_CONFIG') or 'config.yml',
    os.getenv('APP_ENV') or 'default'
)
app.app_context().push()
