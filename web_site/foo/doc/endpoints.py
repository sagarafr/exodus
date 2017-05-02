# -*- coding: utf8 -*-

from __future__ import unicode_literals

import os.path

from flask import redirect, send_from_directory, url_for

from . import doc


@doc.route('/')
def root():
    return redirect(url_for('doc.documentation', filename='index.html'))


@doc.route('/<path:filename>')
def documentation(filename):
    return send_from_directory(
        os.path.join(doc.root_path, 'doc_files'), filename)
