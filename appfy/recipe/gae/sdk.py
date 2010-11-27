# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory.

Options
~~~~~~~

:url: URL to the App Engine SDK file.
:destination: Destination of the extracted SDK. Default is the parts directory.
:clear-destination: If `true`, deletes the destination dir before
    extracting the download. Default is `true`.

Example
~~~~~~~

::

  [gae_sdk]
  # Dowloads and extracts the App Engine SDK.
  recipe = appfy.recipe.gae:sdk
  url = http://googleappengine.googlecode.com/files/google_appengine_1.3.5.zip
  destination = ${buildout:parts-directory}
  hash-name = false
  clear-destination = true
"""
import os

from appfy.recipe.download import Recipe as DownloadRecipe


class Recipe(DownloadRecipe):
    def __init__(self, buildout, name, options):
        parts_dir = os.path.abspath(buildout['buildout']['parts-directory'])
        options.setdefault('destination', parts_dir)
        options.setdefault('clear-destination', 'true')
        super(Recipe, self).__init__(buildout, name, options)
