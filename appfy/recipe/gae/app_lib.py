# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:app_lib
------------------------
Downloads libraries from PyPi and installs in the app directory. This recipe
extends `zc.recipe.egg.Eggs <http://pypi.python.org/pypi/zc.recipe.egg>`_,
so all the options from that recipe are also valid.

Options
~~~~~~~

:eggs: Package names to be installed.
:lib-directory: Destination directory for the libraries. Default is
    `distlib`.
:use-zipimport: If `true`, a zip file with the libraries is created
    instead of a directory. The zip filename will be the value of
    `lib-directory` plus `.zip`.
:ignore-globs: A list of glob patterns to not be copied from the library.
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

Use a different directory for extra libraries instead of this one."""


class Recipe(zc.recipe.egg.Eggs):
    def __init__(self, buildout, name, opts):
        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        # Unzip eggs by default or we can't use some.
        opts.setdefault('unzip', 'true')

        self.parts_dir = buildout['buildout']['parts-directory']

        self.checksum_file = os.path.join(self.parts_dir, 'checksum_%s.txt' %
            name)

        lib_dir = opts.get('lib-directory', 'distlib')
        self.lib_dir = os.path.abspath(lib_dir)

        self.use_zip = opts.get('use-zipimport', 'false') == 'true'
        if self.use_zip:
            self.lib_dir += '.zip'

        # Set list of patterns to be ignored.
        self.ignore = [i for i in opts.get('ignore-globs', '') \
            .split('\n') if i.strip()]

        self.copy_to_app = opts.get('copy-to-app', 'true') == 'true'
        if self.copy_to_app:
            self.delete_safe = opts.get('delete-safe', 'true') != 'false'
        else:
            self.delete_safe = False
            self.app_lib_dir = self.lib_dir
            self.lib_dir = os.path.join(self.parts_dir, lib_dir)

        opts.setdefault('eggs', '')
        super(Recipe, self).__init__(buildout, name, opts)

    def install(self):
        # Get all installed packages.
        reqs, ws = self.working_set()
        paths = self.get_package_paths(ws)

        if self.copy_to_app:
            self.install_in_app_dir(paths)
        else:
            self.install_in_parts_dir(paths)

        return super(Recipe, self).install()

    update = install

    def install_in_app_dir(self, paths):
        # Create temporary directory and zip names.
        id = uuid.uuid4().hex
        tmp_dir = os.path.join(tempfile.gettempdir(), 'TMP_%s' % id)
        tmp_zip = os.path.join(tempfile.gettempdir(), 'TMP_%s.zip' % id)

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
            f.write(LIB_README)
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

    def install_in_parts_dir(self, paths):
        """Still unsupported.

        This option triggers this:

        copy-to-app = false

        The idea is to move the libs to the app only during deployment.
        """
        self.delete_libs()
        os.mkdir(self.lib_dir)
        for name, src in paths:
            dst = os.path.join(self.lib_dir, name)
            self.logger.info('Copying %r...' % name)
            copytree(src, dst, ignore=ignore_patterns(*self.ignore))

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
            tmp_zip = os.path.join(tempfile.gettempdir(), 'TMP_%s.zip' % id)
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
