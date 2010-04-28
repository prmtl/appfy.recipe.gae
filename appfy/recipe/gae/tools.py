"""
appfy.recipe.gae:tools
----------------------

Installs appcfg, dev_appserver and python executables in the buildout
directory. It also allows to set default values to start the dev_appserver.

This recipe extends `zc.recipe.egg <http://pypi.python.org/pypi/zc.recipe.egg>`_
so all the options from that recipe are also valid.

Options
~~~~~~~

:sdk-directory: path to the App Engine SDK directory. It can be an
    absolute path or a reference to the `appfy.recipe.gae:sdk` destination
    option. Default is `${buildout:parts-directory}/google_appengine`.
:dev_appserver-script: path to the dev_appserver script. Default is
    `${buildout:bin-directory}/dev_appserver`.
:appcfg-script: path to the appcfg script. Default is
    `${buildout:bin-directory}/appcfg`.


Example
~~~~~~~

::

  [gae_tools]
  # Installs appcfg, dev_appserver and python executables in the bin directory.
  recipe = appfy.recipe.gae:tools
  sdk-directory = ${gae_sdk:destination}


Note that this example references an `gae_sdk` section from the
`appfy.recipe.gae:sdk` example. An absolute path could also be used.

To set default values to start the dev_appserver, create a section
`dev_appserver` in buildout.cfg. For example:

::

  [dev_appserver]
  # Set default values to start the dev_appserver. All options from the
  # command line are allowed. They are inserted at the beginning of the
  # arguments. Values are used as they are; don't use variables here.
  defaults = --datastore_path=var --history_path=var --blobstore_path=var app


These options can be set in a single line as well. If an option is provided
when calling dev_appserver, it will override the default value if it is set.
"""
import logging
import os

import zc.recipe.egg

from appfy.recipe import get_relative_path


BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.realpath(__file__))))))


class Recipe(zc.recipe.egg.Scripts):
    def __init__(self, buildout, name, opts):
        bin_dir = buildout['buildout']['bin-directory']
        parts_dir = buildout['buildout']['parts-directory']

        # Set default values.
        join = os.path.join
        abspath = os.path.abspath
        opts.setdefault('sdk-directory', join(parts_dir, 'google_appengine'))
        opts.setdefault('dev_appserver-script', join(bin_dir, 'dev_appserver'))
        opts.setdefault('appcfg-script', join(bin_dir, 'appcfg'))
        opts.setdefault('interpreter', 'python')
        opts.setdefault('extra-paths', '')
        opts.setdefault('eggs', '')

        # Set normalized paths.
        self.sdk_dir = abspath(opts['sdk-directory'])
        self.server_script = abspath(opts['dev_appserver-script'])
        self.appcfg_script = abspath(opts['appcfg-script'])

        # Add the SDK and this recipe package to the path.
        opts['extra-paths'] += '\n%s\n%s' % (BASE, self.sdk_dir)

        # Set a flag to use relative paths.
        self.use_rel_paths = opts.get('relative-paths',
            buildout['buildout'].get('relative-paths', 'false')) == 'true'

        super(Recipe, self).__init__(buildout, name, opts)

    def install(self):
        """Creates the scripts."""
        scripts = 'appfy.recipe.gae.scripts'

        self.options.update({
            'entry-points':   '%s=%s:appcfg %s=%s:dev_appserver' % (
                self.appcfg_script, scripts, self.server_script, scripts),
            'initialization': 'gae = %s' % self.get_path(self.sdk_dir),
            'arguments':      'base, gae',
        })

        return super(Recipe, self).install()

    def get_path(self, path):
        if self.use_rel_paths is True:
            return get_relative_path(path, self.buildout['buildout']
                ['directory'])
        else:
            return '%r' % os.path.abspath(path)

    update = install
