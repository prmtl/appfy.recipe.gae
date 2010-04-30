# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:tools
----------------------

Installs a python executable and several SDK scripts in the buildout
directory: appcfg, bulkload_client, bulkloader, dev_appserver and
remote_api_shell.

It also allows to set default values to start the dev_appserver.

This recipe extends `zc.recipe.egg <http://pypi.python.org/pypi/zc.recipe.egg>`_
so all the options from that recipe are also valid.

Options
~~~~~~~

:sdk-directory: Path to the App Engine SDK directory. It can be an
    absolute path or a reference to the `appfy.recipe.gae:sdk` destination
    option. Default is `${buildout:parts-directory}/google_appengine`.
:appcfg-script: Name of the appcfg script to be installed in the bin
    directory.. Default is `appcfg`.
:bulkload_client-script: Name of the bulkloader script to be installed in
    the bin directory. Default is `bulkload_client`.
:bulkloader-script: Name of the bulkloader script to be installed in
    the bin directory. Default is `bulkloader`.
:dev_appserver-script: Name of the dev_appserver script to be installed in
    the bin directory. Default is `dev_appserver`.
:remote_api_shell-script: Name of the remote_api_shell script to be
    installed in the bin directory. Default is `remote_api_shell`.
:config-file: Configuration file with the default values to use in
    scripts. Default is `script_defaults.cfg`.

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
`dev_appserver` in the defined configuration file (`script_defaults.cfg` by
default). For example::

  [dev_appserver]
  # Set default values to start the dev_appserver. All options from the
  # command line are allowed. They are inserted at the beginning of the
  # arguments. Values are used as they are; don't use variables here.
  defaults =
      --datastore_path=var
      --history_path=var
      --blobstore_path=var
      app


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
        # Set default values.
        opts.setdefault('sdk-directory', os.path.join(buildout['buildout']
            ['parts-directory'], 'google_appengine'))
        opts.setdefault('config-file', os.path.join(buildout['buildout']
            ['directory'], 'script_defaults.cfg'))
        opts.setdefault('appcfg-script',           'appcfg')
        opts.setdefault('bulkload_client-script',  'bulkload_client')
        opts.setdefault('bulkloader-script',       'bulkloader')
        opts.setdefault('dev_appserver-script',    'dev_appserver')
        opts.setdefault('remote_api_shell-script', 'remote_api_shell')
        opts.setdefault('interpreter', 'python')
        opts.setdefault('extra-paths', '')
        opts.setdefault('eggs', '')

        # Set normalized paths.
        self.config_file = os.path.abspath(opts['config-file'])
        self.sdk_dir = os.path.abspath(opts['sdk-directory'])

        # Set the scripts to be generated.
        self.scripts = [
            ('appcfg',           opts['appcfg-script']),
            ('bulkload_client',  opts['bulkload_client-script']),
            ('bulkloader',       opts['bulkloader-script']),
            ('dev_appserver',    opts['dev_appserver-script']),
            ('remote_api_shell', opts['remote_api_shell-script']),
        ]

        # Add the SDK and this recipe package to the path.
        opts['extra-paths'] += '\n%s\n%s' % (BASE, self.sdk_dir)

        # Set a flag to use relative paths.
        self.use_rel_paths = opts.get('relative-paths',
            buildout['buildout'].get('relative-paths', 'false')) == 'true'

        super(Recipe, self).__init__(buildout, name, opts)

    def install(self):
        """Creates the scripts."""
        m = 'appfy.recipe.gae.scripts'
        entry_points =['%s=%s:%s' % (n, m, s) for n, s in self.scripts]
        initialization = [
            'gae = %s' % self.get_path(self.sdk_dir),
            'cfg = %s' % self.get_path(self.config_file),
        ]

        if self.use_rel_paths is not True:
            # base won't be set if we are using absolute paths.
            initialization.insert(0, 'base = %r' % self.buildout['buildout']
                ['directory'])

        self.options.update({
            'entry-points':   ' '.join(entry_points),
            'initialization': '\n'.join(initialization),
            'arguments':      'base, gae, cfg',
        })

        return super(Recipe, self).install()

    def get_path(self, path):
        if self.use_rel_paths is True:
            return get_relative_path(path, self.buildout['buildout']
                ['directory'])
        else:
            return '%r' % os.path.abspath(path)

    update = install
