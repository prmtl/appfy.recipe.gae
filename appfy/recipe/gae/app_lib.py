# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:app_lib
------------------------
Downloads libraries from PyPi and installs in the app directory. This recipe
extends `zc.recipe.egg.Scripts <http://pypi.python.org/pypi/zc.recipe.egg>`_,
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
:delete-safe: If `true`, always move `lib-directory` to a temporary directory
    inside the parts dir as a backup when building, instead of deleting it.
    This is to avoid accidental deletion if `lib-directory` is badly
    configured. Default to `true`.

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
import datetime
import logging
import os
import shutil
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


class Recipe(zc.recipe.egg.Scripts):
    def __init__(self, buildout, name, opts):
        # Set a logger with the section name.
        self.logger = logging.getLogger(name)

        # Unzip eggs by default or we can't use some.
        opts.setdefault('unzip', 'true')

        self.parts_dir = buildout['buildout']['parts-directory']
        self.temp_dir = os.path.join(self.parts_dir, 'temp')

        lib_dir = opts.get('lib-directory', 'distlib')
        self.lib_path = os.path.abspath(lib_dir)

        self.use_zip = opts.get('use-zipimport', 'false') == 'true'
        if self.use_zip:
            self.lib_path += '.zip'

        # Set list of patterns to be ignored.
        self.ignore = [i for i in opts.get('ignore-globs', '') \
            .split('\n') if i.strip()]

        self.copy_to_app = opts.get('copy-to-app', 'true') == 'true'
        if self.copy_to_app:
            self.delete_safe = opts.get('delete-safe', 'true') != 'false'
        else:
            # Still unsupported.
            self.delete_safe = False
            self.app_lib_dir = self.lib_path
            self.lib_path = os.path.join(self.parts_dir, lib_dir)

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
        # Delete old libs.
        self.delete_libs()

        if self.use_zip:
            # Create temporary directory for the zip files.
            tmp_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
        else:
            tmp_dir = self.lib_path

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        # Copy all files.
        for name, src in paths:
            self.logger.info('Copying %r...' % name)
            dst = os.path.join(tmp_dir, name)
            copytree(src, dst, ignore=ignore_patterns(*self.ignore))

        # Save README.
        f = open(os.path.join(tmp_dir, 'README.txt'), 'w')
        f.write(LIB_README)
        f.close()

        if self.use_zip:
            # Zip file and remove temporary dir.
            zipdir(tmp_dir, self.lib_path)
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir)

    def install_in_parts_dir(self, paths):
        """Still unsupported.

        This option triggers this:

        copy-to-app = false

        The idea is to move the libs to the app only during deployment.
        """
        return
        self.delete_libs()
        os.mkdir(self.lib_path)
        for name, src in paths:
            dst = os.path.join(self.lib_path, name)
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
        """If the `delete-safe` option is set to true, move the old libraries
        directory to a temporary directory inside the parts dir instead of
        deleting it.
        """
        if not os.path.exists(self.lib_path):
            # Nothing to delete, so it is safe.
            return

        if self.delete_safe is True:
            # Move directory or zip to temporary backup directory.
            if not os.path.exists(self.temp_dir):
                os.mkdir(self.temp_dir)

            date = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S')
            filename = os.path.basename(self.lib_path.rstrip(os.sep))
            if self.use_zip:
                filename = filename[:-4] + date + '.zip'
            else:
                filename += date

            dst = os.path.join(self.temp_dir, filename)
            shutil.move(self.lib_path, dst)
            self.logger.info('Saved libraries backup in %r.' % dst)
        else:
            # Simply delete the directory or zip.
            if self.use_zip:
                os.remove(self.lib_path)
                self.logger.info('Removed lib-zip %r.' % self.lib_path)
            else:
                # Delete the directory.
                shutil.rmtree(self.lib_path)
                self.logger.info('Removed lib-directory %r.' % self.lib_path)
