# from http://pypi.python.org/pypi/hexagonit.recipe.download
import logging
import os.path
import shutil
import tempfile
import urlparse

import zc.buildout
from zc.buildout.download import ChecksumError, Download

import setuptools.archive_util

from appfy.recipe.utils import get_bool_option, get_checksum


class Recipe(object):
    """Recipe for downloading packages from the net and extracting them on
    the filesystem.
    """
    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        self.download_cache = buildout['buildout'].setdefault('download-cache',
            os.path.join(buildout['buildout']['directory'], 'downloads'))

        # All options
        self.option_url = options.get('url')
        self.option_md5sum = options.get('md5sum')
        self.option_sha1sum = options.get('sha1sum')
        self.option_destination = options.setdefault('destination',
            os.path.join(buildout['buildout']['parts-directory'], self.name))
        self.option_clear_destination = get_bool_option(
            options.setdefault('clear-destination', 'false'))
        self.option_strip_top_level_dir = get_bool_option(
            options.setdefault('strip-top-level-dir', 'false'))
        self.option_download_only = get_bool_option(
            options.setdefault('download-only', 'false'))
        self.option_hash_name = get_bool_option(
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
                    # See http://github.com/hexagonit/hexagonit.recipe.download/issues#issue/2
                    filename = os.path.basename(urlparse.urlparse(self.option_url)[2])

                # Copy the file to destination without extraction
                target_path = os.path.join(self.option_destination, filename)
                shutil.copy(cached_path, target_path)
                if not self.option_destination in parts:
                    parts.append(target_path)
            else:
                # Extract the package
                extract_dir = tempfile.mkdtemp("buildout-" + self.name)
                try:
                    setuptools.archive_util.unpack_archive(cached_path,
                        extract_dir)
                except setuptools.archive_util.UnrecognizedFormat:
                    self.logger.error('Unable to extract the package %s. '
                        'Unknown format.', cached_path)
                    raise zc.buildout.UserError('Package extraction error')

                base = self.calculate_base(extract_dir)

                if not os.path.isdir(self.option_destination):
                    os.makedirs(self.option_destination)

                self.logger.info('Extracting package to %s' %
                    self.option_destination)

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
                            raise zc.buildout.UserError('File or directory '
                                'already exists.')
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
        pass

    def calculate_base(self, extract_dir):
        """
        recipe authors inheriting from this recipe can override this method
        to set a different base directory.
        """
        # Move the contents of the package in to the correct destination
        top_level_contents = os.listdir(extract_dir)
        if self.option_strip_top_level_dir:
            if len(top_level_contents) != 1:
                self.logger.error('Unable to strip top level directory '
                    'because there are more than one element in the root '
                    'of the package.')
                raise zc.buildout.UserError('Invalid package contents')

            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        return base

    def download(self):
        d = Download(self.buildout['buildout'],
            hash_name=self.option_hash_name)
        cached_path, is_temp = d(self.option_url, md5sum=self.option_md5sum)

        if self.option_sha1sum and \
            self.option_sha1sum != get_checksum(cached_path):
            raise ChecksumError('SHA1 checksum mismatch for cached download '
                'from %r at %r' % (self.option_url, cached_path))

        return cached_path, is_temp
