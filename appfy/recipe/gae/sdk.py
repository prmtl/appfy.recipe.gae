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
import shutil
import tempfile
import urllib2
import urlparse

from setuptools import archive_util
from zc import buildout
from zc.buildout import download

from appfy.recipe import utils


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


class Recipe(object):
    """Downloads and extracts GAE SDK

    Reuses code from https://pypi.python.org/pypi/hexagonit.recipe.download
    """

    def __init__(self, buildout, name, options):
        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        self.options = options
        self.buildout = buildout
        self.name = name

        parts_dir = os.path.abspath(buildout['buildout']['parts-directory'])
        self.options.setdefault('destination', parts_dir)
        self.options.setdefault('clear-destination', 'true')

        if self.options.get('url') is None:
            self.options['url'] = self.find_latest_sdk_url()

        self.logger.info('Using SDK version found at %s', self.options['url'])

        default_download_cache = os.path.join(
            buildout['buildout']['directory'], 'downloads')
        self.download_cache = buildout['buildout'].setdefault(
            'download-cache', default_download_cache)

        self.option_url = options.get('url')
        self.option_md5sum = options.get('md5sum')
        self.option_sha1sum = options.get('sha1sum')
        default_destinantion = os.path.join(
            buildout['buildout']['parts-directory'], self.name)
        self.option_destination = options.setdefault(
            'destination', default_destinantion)
        self.option_clear_destination = utils.get_bool_option(
            options.setdefault('clear-destination', 'false'))
        self.option_strip_top_level_dir = utils.get_bool_option(
            options.setdefault('strip-top-level-dir', 'false'))
        self.option_download_only = utils.get_bool_option(
            options.setdefault('download-only', 'false'))
        self.option_hash_name = utils.get_bool_option(
            options.setdefault('hash-name', 'false'))
        self.option_filename = options.get('filename', '').strip()

    def install(self):
        if not os.path.exists(self.download_cache):
            os.makedirs(self.download_cache)

        cached_path, is_temp = self.download()

        parts = []

        try:
            # Create destination directory
            if not os.path.isdir(self.option_destination):
                os.makedirs(self.option_destination)
                parts.append(self.option_destination)

            if self.option_download_only:
                if self.option_filename:
                    # Use an explicit filename from the section configuration
                    filename = self.option_filename
                else:
                    # Use the original filename of the downloaded file
                    # regardless whether download filename hashing is enabled.
                    # http://github.com/hexagonit/hexagonit.recipe.download/issues#issue/2
                    filename = os.path.basename(
                        urlparse.urlparse(self.option_url)[2])

                # Copy the file to destination without extraction
                target_path = os.path.join(self.option_destination, filename)
                shutil.copy(cached_path, target_path)
                if self.option_destination not in parts:
                    parts.append(target_path)
            else:
                # Extract the package
                extract_dir = tempfile.mkdtemp("buildout-" + self.name)
                try:
                    archive_util.unpack_archive(
                        cached_path, extract_dir)
                except archive_util.UnrecognizedFormat:
                    self.logger.error(
                        'Unable to extract the package %s. Unknown format.',
                        cached_path)
                    raise buildout.UserError('Package extraction error')

                base = self.calculate_base(extract_dir)

                if not os.path.isdir(self.option_destination):
                    os.makedirs(self.option_destination)

                self.logger.info(
                    'Extracting package to %s', self.option_destination)

                for filename in os.listdir(base):
                    dest = os.path.join(self.option_destination, filename)
                    if os.path.exists(dest):
                        if self.option_clear_destination:
                            shutil.rmtree(dest)
                            self.logger.info('Removed: %r.' % dest)
                            parts.append(dest)
                        else:
                            self.logger.error(
                                'Target %s already exists. Either remove it '
                                'or set ``clear-destination = true`` in your '
                                'buildout.cfg to remove existing files and '
                                'directories before moving downloaded files.',
                                dest)
                            raise buildout.UserError(
                                'File or directory already exists.')
                    else:
                        # Only add the file/directory to the list of installed
                        # parts if it does not already exist. This way it does
                        # not get accidentally removed when uninstalling.
                        parts.append(dest)

                    if not os.path.exists(dest):
                        shutil.move(os.path.join(base, filename), dest)

                shutil.rmtree(extract_dir)

        finally:
            if is_temp:
                os.unlink(cached_path)

        return parts

    def update(self):
        # TODO(prmtl): on update we can check if there is a new SDK avaiable
        pass

    def calculate_base(self, extract_dir):
        """Get base directory

        """
        # Move the contents of the package in to the correct destination
        top_level_contents = os.listdir(extract_dir)
        if self.option_strip_top_level_dir:
            if len(top_level_contents) != 1:
                self.logger.error(
                    'Unable to strip top level directory '
                    'because there are more than one element in the root '
                    'of the package.')
                raise buildout.UserError('Invalid package contents')

            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        return base

    def download(self):
        d = download.Download(
            self.buildout['buildout'],
            hash_name=self.option_hash_name)
        cached_path, is_temp = d(self.option_url, md5sum=self.option_md5sum)

        if (self.option_sha1sum and
           self.option_sha1sum != utils.get_checksum(cached_path)):
            raise download.ChecksumError(
                'SHA1 checksum mismatch for cached download '
                'from %r at %r' % (self.option_url, cached_path))

        return cached_path, is_temp

    # TODO(prmtl): change name
    @classmethod
    def find_latest_sdk_url(cls):
        """Returns latest avaiable Python SDK url

        If there are no SDKs found, SDKCouldNotBeFound will be raised
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
        """Checks if SDK under given URL is avaiable do download

        Check is done by performing a HEAD request to the URL and if
        there is no error, SDK is avaiable to download.
        """
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
