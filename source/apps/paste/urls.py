# -*- coding: utf-8 -*-
"""
    apps.paste.urls
    ~~~~~~~~~~~~~~~

    URL definitions.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
from tipfy import Rule, Submount

def get_rules():
    rules = [
        Submount('/paste', [
            Rule('/', endpoint='paste/new', handler='apps.paste.handlers.PasteNewHandler', subdomain='<area_name>'),
            Rule('/+<language>', endpoint='paste/new', handler='apps.paste.handlers.PasteNewHandler', subdomain='<area_name>'),
            Rule('/view/<int:paste_id>', endpoint='paste/view', handler='apps.paste.handlers.PasteViewHandler', subdomain='<area_name>'),
        ]),
    ]

    return rules
