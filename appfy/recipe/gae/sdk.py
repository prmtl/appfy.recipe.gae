# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory.

Options
~~~~~~~

:url: URL to the App Engine SDK file. Default is to download the latest version
    from storage.googleapis.com.
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
import urllib2
import xml.etree.ElementTree as et
import distutils.version as version
import re

from appfy.recipe.download import Recipe as DownloadRecipe


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


class SDKCouldNotBeFound(Exception):
    pass


class Recipe(DownloadRecipe):
    def __init__(self, buildout, name, options):
        parts_dir = os.path.abspath(buildout['buildout']['parts-directory'])
        options.setdefault('destination', parts_dir)
        options.setdefault('clear-destination', 'true')
        super(Recipe, self).__init__(buildout, name, options)

    def install(self):
        if self.option_url is None:
            self.option_url = self.find_latest_sdk_url()
            self.logger.info('Using latest GAE SDK from "{}"'.format(self.option_url))
        return super(Recipe, self).install()

    def find_latest_sdk_url(self):
        base = 'https://storage.googleapis.com/appengine-sdks/'
        ns = '{http://doc.s3.amazonaws.com/2006-03-01}'
        featured_re = re.compile(r'featured/google_appengine_(\d+\.\d+\.\d+).zip')

        tree = et.parse(urllib2.urlopen(base))
        keys = (contents.find(ns + 'Key') for contents in tree.getroot().findall(ns + 'Contents'))
        candidates = ((el, featured_re.match(el.text)) for el in keys)
        candidates = ((el, match.group(1)) for el, match in candidates if not match is None)
        candidates = ((el, version.StrictVersion(version_str)) for el, version_str in candidates)

        # Sort latest to oldest by version number
        candidates = sorted(candidates, key=lambda tup: tup[1], reverse=True)
        urls = (''.join([base, el.text]) for el, version in candidates)

        # Newest listed versions are not immediately available to download. Check over HEAD.
        for url in urls:
            try:
                request = HeadRequest(url)
                urllib2.urlopen(request)
            except urllib2.HTTPError as e:
                if e.code == 403:
                    pass  # Not yet public.
                else:
                    raise
            else:
                return url
        raise SDKCouldNotBeFound('Could not find a usable SDK version automatically')
