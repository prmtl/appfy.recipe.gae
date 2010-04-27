"""
"""
import logging
import os
import shutil
import zc.buildout

import hexagonit.recipe.download


class Recipe(hexagonit.recipe.download.Recipe):
    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        self.destination = options.get('destination', os.path.join(
            buildout['buildout']['parts-directory'], name))

        if not os.path.isabs(self.destination):
            self.destination = os.path.abspath(self.destination)

        self.clear = options.get('clear-destination', 'false') == 'true'

        super(Recipe, self).__init__(buildout, name, options)

    def install(self):
        if self.clear:
            removed = False
            if os.path.isdir(self.destination):
                shutil.rmtree(self.destination)
                removed = True
            elif os.path.isfile(self.destination):
                os.remove(self.destination)
                removed = True

            if removed is True:
                self.logger.info('Removed App Engine SDK %r.' % \
                    self.destination)

        return super(Recipe, self).install()

    update = install
