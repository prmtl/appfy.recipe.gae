# -*- coding: utf-8 -*-
"""
    apps.paste.highlighting
    ~~~~~~~~~~~~~~~~~~~~~~~

    Highlighting helpers. Adapted from LodgeIt:
    http://dev.pocoo.org/projects/lodgeit/

    :copyright: 2007 by Armin Ronacher.
    :license: BSD
"""
import re
import pygments
import csv
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename, \
     get_lexer_for_mimetype, PhpLexer, TextLexer
from pygments.styles import get_all_styles
from pygments.formatters import HtmlFormatter

from werkzeug import escape

from tipfy import local
from tipfy.ext.i18n import lazy_gettext as _

#: we use a hardcoded list here because we want to keep the interface
#: simple
LANGUAGES = {
    'text':             _('Text'),
    #'multi':            _('Multi-File'),
    'python':           _('Python'),
    'pycon':            _('Python Console Sessions'),
    'pytb':             _('Python Tracebacks'),
    'html+php':         _('PHP'),
    #'php':              _('PHP (inline)'),
    'html+django':      _('Django / Jinja Templates'),
    'html+mako':        _('Mako Templates'),
    'html+myghty':      _('Myghty Templates'),
    'apache':           _('Apache Config (.htaccess)'),
    'bash':             _('Bash'),
    'bat':              _('Batch (.bat)'),
    'brainfuck':        _('Brainfuck'),
    'c':                _('C'),
    #'gcc-messages':     _('GCC Messages'),
    'cpp':              _('C++'),
    'csharp':           _('C#'),
    'css':              _('CSS'),
    #'csv':              _('CSV'),
    'd':                _('D'),
    'minid':            _('MiniD'),
    'smarty':           _('Smarty'),
    'glsl':             _('GL Shader language'),
    'html':             _('HTML'),
    'html+genshi':      _('Genshi Templates'),
    'js':               _('JavaScript'),
    'java':             _('Java'),
    #'javac-messages':   _('javac Messages'),
    'jsp':              _('JSP'),
    'lua':              _('Lua'),
    'haskell':          _('Haskell'),
    'literate-haskell': _('Literate Haskell'),
    'scheme':           _('Scheme'),
    'ruby':             _('Ruby'),
    'irb':              _('Interactive Ruby'),
    'ini':              _('INI File'),
    'perl':             _('Perl'),
    'rhtml':            _('eRuby / rhtml'),
    'tex':              _('TeX / LaTeX'),
    'xml':              _('XML'),
    'rst':              _('reStructuredText'),
    'irc':              _('IRC Logs'),
    #'diff':             _('Unified Diff'),
    'vim':              _('Vim Scripts'),
    'ocaml':            _('OCaml'),
    'sql':              _('SQL'),
    'mysql':            _('MySQL'),
    'squidconf':        _('SquidConf'),
    'sourceslist':      _('sources.list'),
    'erlang':           _('Erlang'),
    'vim':              _('Vim'),
    'dylan':            _('Dylan'),
    'gas':              _('GAS'),
    'nasm':             _('Nasm'),
    'llvm':             _('LLVM'),
    #'creole':           _('Creole Wiki'),
    'clojure':          _('Clojure'),
    'io':               _('IO'),
    'objectpascal':     _('Object-Pascal'),
    'scala':            _('Scala'),
    'boo':              _('Boo'),
    'matlab':           _('Matlab'),
    'matlabsession':    _('Matlab Session'),
    'povray':           _('Povray'),
    'smalltalk':        _('Smalltalk'),
    'control':          _('Debian control-files'),
    'gettext':          _('Gettext catalogs'),
    'lighttpd':         _('Lighttpd'),
    'nginx':            _('Nginx'),
    'yaml':             _('YAML'),
    'xslt':             _('XSLT'),
    'go':               _('Go'),
}

STYLES = dict((x, x.title()) for x in get_all_styles())

DEFAULT_STYLE = 'friendly'


def get_language_name(code):
    """Language name, based on the language code."""
    return str(LANGUAGES.get(code, _('Undefined language')))


def list_languages():
    """List all languages."""
    languages = LANGUAGES.items()
    languages.sort(key=lambda x: str(x[1]).lstrip(' _-.').lower())
    return languages


def get_style(request=None, name_only=False):
    """Style for a given request or style name."""
    if request is None:
        request = local.request
    if isinstance(request, basestring):
        style_name = request
    else:
        style_name = request.cookies.get('paste.style', DEFAULT_STYLE)
    try:
        f = HtmlFormatter(style=style_name)
    except ClassNotFound:
        style_name = DEFAULT_STYLE
        f = HtmlFormatter(style=style_name)
    if name_only:
        return style_name
    return style_name, f.get_style_defs(('#paste', '.syntax'))


def highlight(code, language, _preview=False):
    """Highlight a given code to HTML."""
    code = u'\n'.join(code.splitlines())
    """
    # TODO - from lodgeit, not implemented here
    if not _preview:
        if language == 'diff':
            return highlight_diff(code)
        elif language == 'creole':
            return format_creole(code)
        elif language == 'csv':
            return format_csv(code)
        elif language == 'gcc-messages':
            return format_compiler_messages(parse_gcc_messages(code), 'gcc')
        elif language == 'javac-messages':
            return format_compiler_messages(parse_javac_messages(code), 'javac')
    if language == 'multi':
        return highlight_multifile(code)
    elif language == 'php':
        lexer = PhpLexer(startinline=True)
    else:
    """
    try:
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        lexer = TextLexer()
    style = get_style(name_only=True)
    formatter = HtmlFormatter(linenos=True, cssclass='syntax', style=style)
    return u'<div class="highlight">%s</div>' % \
           pygments.highlight(code, lexer, formatter)
