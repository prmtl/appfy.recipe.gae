"""
Options
=======
sdk-directory
dev_appserver-script
appcfg-script
"""
import logging
import os
import zc.recipe.egg

from appfy.recipe import get_relative_path


BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
    os.path.realpath(__file__)))))


class Recipe(zc.recipe.egg.Scripts):
    def __init__(self, buildout, name, opts):
        bin_dir = buildout['buildout']['bin-directory']
        parts_dir = buildout['buildout']['parts-directory']

        # Set default values.
        join = os.path.join
        opts.setdefault('sdk-directory', join(parts_dir, 'google_appengine'))
        opts.setdefault('dev_appserver-script', 'dev_appserver')
        opts.setdefault('appcfg-script', 'appcfg')

        # Set normalized paths.
        self.sdk_dir = os.path.abspath(opts['sdk-directory'])

        self.server_script = opts['dev_appserver-script']
        if not os.path.isabs(self.server_script):
            self.server_script = join(bin_dir, self.server_script)

        self.appcfg_script = opts['appcfg-script']
        if not os.path.isabs(self.appcfg_script):
            self.appcfg_script = join(bin_dir, self.appcfg_script)

        # Install python interpreter with the SDK and this recipe package
        # in the path.
        opts.setdefault('interpreter', 'python')
        opts.setdefault('extra-paths', '')
        opts.setdefault('eggs', '')
        opts['extra-paths'] += '\n%s\n%s' % (BASE, self.sdk_dir)
        #opts['extra-paths'] += '\n%s' % (BASE,)

        self.use_rel_paths = opts.get('relative-paths',
            buildout['buildout'].get('relative-paths', 'false')) == 'true'

        super(Recipe, self).__init__(buildout, name, opts)

    def install(self):
        """Creates the scripts."""
        scripts = 'appfy.recipe.scripts'
        sdk_dir = self.get_path(self.sdk_dir)

        entry_points = '%s=%s:appcfg %s=%s:dev_appserver' % (
            self.appcfg_script, scripts, self.server_script, scripts)

        self.options.update({
            'entry-points':   '%s=%s:appcfg %s=%s:dev_appserver' % (
                self.appcfg_script, scripts, self.server_script, scripts),
            'initialization': 'gae = %s' % sdk_dir,
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
