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
from distutils import version
import json
import logging
import os
import re
import urllib2

from appfy.recipe import download


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


class SDKCouldNotBeFound(Exception):
    pass


class Recipe(download.Recipe):

    # Eg. featured/google_appengine_1.9.14.zip
    PYTHON_SDK_RE = re.compile(
        r'featured/google_appengine_(\d+\.\d+\.\d+).zip'
    )
    URL = ("https://www.googleapis.com/storage/"
           "v1/b/appengine-sdks/o?prefix=featured")

    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)

        parts_dir = os.path.abspath(buildout['buildout']['parts-directory'])
        options.setdefault('destination', parts_dir)
        options.setdefault('clear-destination', 'true')

        if options.get('url') is None:
            options['url'] = self.find_latest_sdk_url()

        self.logger.info('Using SDK version found at %s', options['url'])

        super(Recipe, self).__init__(buildout, name, options)

    def find_latest_sdk_url(self):
        def version_key(sdk):
            version_string = self.PYTHON_SDK_RE.match(sdk['name']).group(1)
            return version.StrictVersion(version_string)

        raw_bucket_list = urllib2.urlopen(self.URL).read()
        bucket_list = json.loads(raw_bucket_list)

        all_sdks = bucket_list['items']
        python_sdks = [
            sdk for sdk in all_sdks if self.PYTHON_SDK_RE.match(sdk['name'])
        ]

        # 1.9.14 > 1.9.13 so we need reverse order
        python_sdks.sort(key=version_key, reverse=True)

        # Newest listed versions are not immediately available to download.
        # Check over HEAD.
        for sdk in python_sdks:
            url = str(sdk['mediaLink'])
            try:
                request = HeadRequest(url)
                urllib2.urlopen(request)
            except urllib2.HTTPError as e:
                # 403 - not yet published, try next one
                if e.code != 403:
                    raise
            else:
                return url
        raise SDKCouldNotBeFound(
            'Could not find a usable SDK version automatically'
        )
