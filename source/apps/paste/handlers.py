# -*- coding: utf-8 -*-
"""
    apps.paste.handlers
    ~~~~~~~~~~~~~~~~~~~

    Handlers for a really simple pastebin.

    :copyright: 2010 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
import tipfy
from tipfy.ext.i18n import _

from apps.base.handlers import AreaRequestHandler

from apps.paste.models import Paste, PasteForm
from apps.paste.highlighting import highlight


class PasteBaseHandler(AreaRequestHandler):
    """Base class for the pastebin."""
    def __init__(self):
        AreaRequestHandler.__init__(self)

        # Set a flag in context for menus.
        self.context['current_app'] = 'paste'

        # Initialize list of breadcrumbs.
        self.breadcrumbs = []

    def get_breadcrumb(self, endpoint, text, **kwargs):
        return (tipfy.url_for(endpoint, area_name=self.area.name, **kwargs),
            text)

    def add_breadcrumb(self, endpoint, text, **kwargs):
        self.breadcrumbs.append(self.get_breadcrumb(endpoint, text, **kwargs))

    def render_response(self, filename, **values):
        self.context['breadcrumbs'] = [
            self.get_breadcrumb('home/index', _('Home')),
            self.get_breadcrumb('paste/new', _('Paste'))] + self.breadcrumbs

        return super(PasteBaseHandler, self).render_response(filename, **values)


class PasteNewHandler(PasteBaseHandler):
    """Displays a paste form and saves a new paste."""
    def get(self, **kwargs):
        language = kwargs.pop('language', 'text')
        form = PasteForm(language=language)

        context = {
            'form': form,
        }
        return self.render_response('paste/new.html', **context)

    def post(self, **kwargs):
        if self.current_user:
            user_key = str(self.current_user.key())
        else:
            user_key = None

        language_code = tipfy.request.form.get('language')
        code_raw = tipfy.request.form.get('code', u'')
        code = highlight(code_raw, language_code)

        values = {
            'area_key': str(self.area.key()),
            'user_key': user_key,
            'code_raw': code_raw,
            'code':     code,
            'language': language_code,
        }
        paste = Paste(**values)
        paste.put()

        return tipfy.redirect_to('paste/view', paste_id=paste.id,
            area_name=self.area.name)


class PasteViewHandler(PasteBaseHandler):
    """Displays a paste."""
    def get(self, **kwargs):
        paste_id = kwargs.pop('paste_id', None)
        if not paste_id:
            raise tipfy.NotFound()

        paste = Paste.get_by_id(paste_id)
        if not paste:
            raise tipfy.NotFound()

        self.add_breadcrumb('paste/view', _('Paste #%s') % paste.id,
            paste_id=paste.id)
        form = PasteForm(code=paste.code_raw, language=paste.language)

        context = {
            'paste': paste,
            'form': form,
        }
        return self.render_response('paste/view.html', **context)


class PasteListHandler(PasteBaseHandler):
    """Not implemented."""
    def get(self, **kwargs):
        context = {
        }
        return self.render_response('paste/new.html', **context)
