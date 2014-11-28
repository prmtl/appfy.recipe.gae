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


# Eg. featured/google_appengine_1.9.14.zip
PYTHON_SDK_RE = re.compile(
    r'featured/google_appengine_(\d+\.\d+\.\d+).zip'
)


SDK_BUCKET_URL = ("https://www.googleapis.com/storage/"
                  "v1/b/appengine-sdks/o?prefix=featured")


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


class SDKCouldNotBeFound(Exception):
    pass


class Recipe(download.Recipe):

    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)

        parts_dir = os.path.abspath(buildout['buildout']['parts-directory'])
        options.setdefault('destination', parts_dir)
        options.setdefault('clear-destination', 'true')

        if options.get('url') is None:
            options['url'] = self.find_latest_sdk_url()

        self.logger.info('Using SDK version found at %s', options['url'])

        super(Recipe, self).__init__(buildout, name, options)

    # TODO(prmtl): change name
    @classmethod
    def find_latest_sdk_url(cls):
        """Returns latest avaiable Python SDK url
        """
        # Newest listed versions are not immediately available to download.
        # Check over HEAD.
        for sdk_url in cls.get_ordered_sdks_urls():
            if cls.is_sdk_avaiable(sdk_url):
                return sdk_url
        else:
            raise SDKCouldNotBeFound(
                'Could not find a usable SDK version automatically'
            )

    @classmethod
    def get_ordered_sdks_urls(cls):
        raw_bucket_list = urllib2.urlopen(SDK_BUCKET_URL).read()
        # TODO(prmtl): test that we cannot decode JSON
        bucket_list = json.loads(raw_bucket_list)

        # TODO(prmtl): test that there is no 'items'
        all_sdks = bucket_list['items']
        python_sdks = [
            sdk for sdk in all_sdks if PYTHON_SDK_RE.match(sdk['name'])
        ]

        python_sdks = cls._sort_sdk_by_version(python_sdks)

        urls = [sdk['mediaLink'] for sdk in python_sdks]

        return urls

    @classmethod
    def _sort_sdk_by_version(cls, sdks):
        """Sorts lists of Python SDKs by version using bucket object name
        """
        def version_key(sdk):
            version_string = PYTHON_SDK_RE.match(sdk['name']).group(1)
            return version.StrictVersion(version_string)

        # 1.9.14 > 1.9.13 so we need reverse order
        return sorted(sdks, key=version_key, reverse=True)

    @classmethod
    def is_sdk_avaiable(cls, url):
        try:
            request = HeadRequest(url)
            urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            # 403, 401 - not yet published, try next one
            if e.code not in (401, 403):
                raise
            return False
        else:
            return True

