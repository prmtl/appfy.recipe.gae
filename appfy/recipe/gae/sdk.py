# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory. This
recipe extends `hexagonit.recipe.download <http://pypi.python.org/pypi/hexagonit.recipe.download>`_
so all the download options from that recipe are also valid.

Options
~~~~~~~

:destination: Destination of the extracted SDK download. Default is
    `${buildout:parts-directory}/google_appengine`.
:clear-destination: If `true`, deletes the destination dir before
    extracting the download. Default is `false`.

Example
~~~~~~~

::

  [gae_sdk]
  # Dowloads and extracts the App Engine SDK.
  recipe = appfy.recipe.gae:sdk
  url = http://googleappengine.googlecode.com/files/google_appengine_1.3.3.zip
  destination = ${buildout:parts-directory}
  hash-name = false
  clear-destination = true
"""
import logging
import os
import shutil

import hexagonit.recipe.download


class Recipe(hexagonit.recipe.download.Recipe):
    def __init__(self, buildout, name, options):
        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        parts_dir = buildout['buildout']['parts-directory']

        # Set options.
        self.destination = os.path.abspath(options.get('destination',
            os.path.join(parts_dir, 'google_appengine')))
        self.clear = options.get('clear-destination', 'false') == 'true'

        super(Recipe, self).__init__(buildout, name, options)

    def install(self):
        if self.clear and os.path.isdir(self.destination):
            shutil.rmtree(self.destination)
            self.logger.info('Removed App Engine SDK %r.' % self.destination)

        return super(Recipe, self).install()

    update = install
