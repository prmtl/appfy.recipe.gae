"""
Options
=======
eggs:
lib-directory:
lib-zip:
ignore-patterns:
primary-lib-directory:
delete-safe: Checks directory destination before deleting. It will require
    manual deletion if the checksum from the last build differs. Default to
    true.
"""
import hashlib
import logging
import os
import shutil
import stat
import tempfile
import uuid
import zc.recipe.egg

from appfy.recipe import copytree, ignore_patterns, zipdir


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

        self.lib_zip = opts.get('lib-zip', None)
        if self.lib_zip and not os.path.isabs(self.lib_zip):
            self.lib_zip = os.path.abspath(self.lib_zip)

        self.primary_lib_dir = opts.get('primary-lib-directory', 'lib')

        # Set list of patterns to be ignored.
        self.ignore = [i for i in opts.get('ignore-patterns', '') \
            .split('\n') if i.strip()]

        # Unused for now. All deletion is safe.
        self.delete_safe = opts.get('delete-safe', 'true') != 'false'

        super(Recipe, self).__init__(buildout, name, opts)

    def install(self):
        reqs, ws = self.working_set()

        # Get all packages.
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
                copytree(src, dst, ignore=ignore_patterns(*self.ignore))

            # Save README.
            f = open(os.path.join(tmp_dir, 'README.txt'), 'w')
            f.write(LIB_README % {'lib_dir': self.primary_lib_dir})
            f.close()

            # Zip temporary directory to a temporary zip and create checksum.
            zipdir(tmp_dir, tmp_zip)
            checksum = self.calculate_checksum(tmp_zip)

            # Delete old libs and move the new ones.
            self.delete_libs()
            if self.lib_zip:
                shutil.copyfile(tmp_zip, self.lib_zip)
                self.logger.info('Copied libraries %r.' % self.lib_zip)
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
        if self.lib_zip:
            lib = self.lib_zip
        else:
            lib = self.lib_dir

        if not os.path.exists(lib):
            # Nothing to delete, so it is safe.
            return

        if self.delete_safe is True:
            msg = "Please delete the libraries manually and try again: %r." \
                "\nAlternatively you can set 'delete-safe = false' in " \
                "buildout.cfg to never check for changes." % lib

            # Compare saved and current checksums.
            old_checksum = self.get_old_checksum()
            if old_checksum is None:
                raise IOError("Missing checksum for the libraries. " + msg)
            elif old_checksum != self.get_new_checksum(lib):
                raise IOError("The checksum for the libraries didn't match. "
                    + msg)

        if self.lib_zip:
            os.remove(lib)
            self.logger.info('Removed lib-zip %r.' % lib)
        else:
            # Delete the directory.
            shutil.rmtree(lib)
            self.logger.info('Removed lib-directory %r.' % lib)

    def get_old_checksum(self):
        if os.path.isfile(self.checksum_file):
            f = open(self.checksum_file, 'r')
            checksum = f.read().strip()
            f.close()

            return checksum

    def get_new_checksum(self, filename):
        if os.path.isdir(filename):
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
