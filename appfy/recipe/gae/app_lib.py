"""
appfy.recipe.gae:app_lib
------------------------
Downloads packages from PyPi and installs in the app directory. This recipe
extends `zc.recipe.egg <http://pypi.python.org/pypi/zc.recipe.egg>`_ so all
the options from that recipe are also valid.

Options
~~~~~~~

:eggs: package names to be installed.
:lib-directory: the destination directory for the libaries. Default is
  `distlib`.
:primary-lib-directory: The main directory used for libraries. This is
  only used to create a README.txt inside `lib-directory` with a warning.
:use-zipimport: If `true`, a zip file with the libraries is created
  instead of a directory. The zip file will use the value of
  `lib-directory` for the filename, plus `.zip`.
:ignore-globs: a list of glob patterns to not be copied from the library.
:delete-safe: Checks the checksum of the destination directory before
  deleting. It will require manual deletion if the checksum from the last
  build differs. Default to true.

Example
~~~~~~~

::

  [app_lib]
  # Sets the library dependencies for the app.
  recipe = appfy.recipe.gae:app_lib
  lib-directory = app/distlib
  use-zipimport = false

  # Define the libraries.
  eggs =
      babel
      jinja2
      wtforms
      werkzeug
      gaepytz
      gaema
      tipfy

  # Don't copy files that match these glob patterns.
  ignore-globs =
      *.c
      *.pyc
      *.pyo
      */test
      */tests
      */testsuite
      */django
      */sqlalchemy
"""
import hashlib
import logging
import os
import shutil
import stat
import tempfile
import uuid

import zc.recipe.egg


from appfy.recipe import (copytree, ignore_patterns, include_patterns,
    rmfiles, zipdir)


BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.realpath(__file__))))))


LIB_README = """Warning!
========

This directory is removed every time the buildout tool runs, so don't place
or edit things here because any changes will be lost!

Use the "%(lib_dir)s" directory to place other libraries or to override
packages from this directory."""


class Recipe(zc.recipe.egg.Scripts):
    def __init__(self, buildout, name, opts):
        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        self.parts_dir = buildout['buildout']['parts-directory']

        self.checksum_file = os.path.join(self.parts_dir, 'checksum_%s.txt' %
            name)

        self.lib_dir = opts.get('lib-directory', 'distlib')
        if not os.path.isabs(self.lib_dir):
            self.lib_dir = os.path.abspath(self.lib_dir)

        self.use_zip = opts.get('use-zipimport', 'false') == 'true'
        if self.use_zip:
            self.lib_dir += '.zip'

        self.primary_lib_dir = opts.get('primary-lib-directory', 'lib')

        # Set list of patterns to be ignored.
        self.ignore = [i for i in opts.get('ignore-globs', '') \
            .split('\n') if i.strip()]

        # Unused for now. All deletion is safe.
        self.delete_safe = opts.get('delete-safe', 'true') != 'false'

        super(Recipe, self).__init__(buildout, name, opts)

    def install(self):
        # Get all installed packages.
        reqs, ws = self.working_set()
        paths = self.get_package_paths(ws)

        # Create temporary directory and zip names.
        id = uuid.uuid4().hex
        tmp_dir = os.path.join(tempfile.tempdir, 'TMP_%s' % id)
        tmp_zip = os.path.join(tempfile.tempdir, 'TMP_%s.zip' % id)

        if os.path.isdir(tmp_dir) or os.path.isfile(tmp_zip):
            raise IOError('Temporary file already exists. Try again.')

        try:
            # Copy all files to temporary dir.
            os.mkdir(tmp_dir)
            for name, src in paths:
                dst = os.path.join(tmp_dir, name)
                self.logger.info('Copying %r...' % name)
                copytree(src, dst, ignore=ignore_patterns(*self.ignore))

            # Save README.
            f = open(os.path.join(tmp_dir, 'README.txt'), 'w')
            f.write(LIB_README % {'lib_dir': self.primary_lib_dir})
            f.close()

            # Zip temporary directory and create checksum.
            zipdir(tmp_dir, tmp_zip)
            checksum = self.calculate_checksum(tmp_zip)

            # Delete old libs and move the new ones.
            self.delete_libs()
            if self.use_zip:
                shutil.copyfile(tmp_zip, self.lib_dir)
            else:
                copytree(tmp_dir, self.lib_dir)

            self.logger.info('Copied libraries %r.' % self.lib_dir)

            # Save current checksum.
            self.save_checksum(checksum)
        finally:
            # Remove temporary directory and zip.
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir)

            if os.path.isfile(tmp_zip):
                os.remove(tmp_zip)

        return super(Recipe, self).install()

    update = install

    def get_package_paths(self, ws):
        """Returns the list of package paths to be copied."""
        pkgs = []
        for path in ws.entries:
            egg_path = os.path.join(path, 'EGG-INFO')
            if not os.path.isdir(egg_path):
                raise IOError('Missing EGG-INFO directory %r.' % egg_path)

            top_path = os.path.join(egg_path, 'top_level.txt')
            if not os.path.isfile(top_path):
                raise IOError('Missing top_level.txt file %r.' % top_path)

            f = open(top_path, 'r')
            lib = f.read().strip()
            f.close()

            pkgs.append((lib, os.path.join(path, lib)))

        return pkgs

    def delete_libs(self):
        if not os.path.exists(self.lib_dir):
            # Nothing to delete, so it is safe.
            return

        if self.delete_safe is True:
            msg = "Please delete the libraries manually and try again: %r." \
                "\nAlternatively you can set 'delete-safe = false' in " \
                "buildout.cfg to never check for changes." % self.lib_dir

            # Compare saved and current checksums.
            old_checksum = self.get_old_checksum()
            if old_checksum is None:
                raise IOError("Missing checksum for the libraries. " + msg)
            elif old_checksum != self.get_new_checksum(self.lib_dir):
                raise IOError("The checksum for the libraries didn't match. "
                    + msg)

        if self.use_zip:
            os.remove(self.lib_dir)
            self.logger.info('Removed lib-zip %r.' % self.lib_dir)
        else:
            # Delete the directory.
            shutil.rmtree(self.lib_dir)
            self.logger.info('Removed lib-directory %r.' % self.lib_dir)

    def get_old_checksum(self):
        if os.path.isfile(self.checksum_file):
            f = open(self.checksum_file, 'r')
            checksum = f.read().strip()
            f.close()

            return checksum

    def get_new_checksum(self, filename):
        if os.path.isdir(filename):
            # Remove *.pyc files to match the old checksum.
            rmfiles(self.lib_dir, only=include_patterns('*.pyc'))
            # Zip first, then calculate checksum.
            id = uuid.uuid4().hex
            tmp_zip = os.path.join(tempfile.tempdir, 'TMP_%s.zip' % id)
            zipdir(filename, tmp_zip)
            checksum = self.calculate_checksum(tmp_zip)
            os.remove(tmp_zip)
        else:
            checksum = self.calculate_checksum(filename)

        return checksum

    def calculate_checksum(self, filename):
        return hashlib.md5(open(filename, 'rb').read()).hexdigest()

    def save_checksum(self, checksum):
        f = open(self.checksum_file, 'w')
        f.write(checksum)
        f.close()
        self.logger.info('Generated libraries checksum %r.' % \
            self.checksum_file)
