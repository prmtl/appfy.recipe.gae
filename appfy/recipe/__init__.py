# -*- coding: utf-8 -*-
"""
appfy.recipe
------------

General utilities shared by all recipes.
"""
import fnmatch
import os
import shutil
import zipfile


def get_relative_path(path, base_path):
    path = os.path.normcase(path)
    base_path = os.path.normcase(base_path)

    original = path
    r = []
    while 1:
        dirname, basename = os.path.split(path)
        r.append(basename)
        if dirname == base_path:
            break

        if dirname == path:
            return '%r' % original

        path = dirname

    r.reverse()
    return 'join(base, %r)' % os.path.join(*r)


def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter.

    Patterns is a sequence of glob-style patterns
    that are used to exclude files

    Adapted from Python 2.6 source.
    """
    def _ignore_patterns(path, names):
        names = [os.path.join(path, name) for name in names]
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))

        return set(ignored_names)
    return _ignore_patterns


include_patterns = ignore_patterns


def rmfiles(src, only=None):
    names = os.listdir(src)

    if only is not None:
        only_names = only(src, names)
    else:
        only_names = set()

    for name in names:
        srcname = os.path.join(src, name)
        if srcname in only_names:
            if os.path.isfile(srcname):
                os.remove(srcname)
            elif os.path.isdir(srcname):
                shutil.rmtree(srcname)
        elif os.path.isdir(srcname):
            rmfiles(srcname, only=only)


def zipdir(dirname, filename):
    assert os.path.isdir(dirname)
    z = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    try:
        for root, dirs, files in os.walk(dirname):
            # NOTE: ignore empty directories
            for f in files:
                absf = os.path.join(root, f)
                zf = absf[len(dirname)+len(os.sep):]
                z.write(absf, zf)

        z.close()
    finally:
        if z:
            z.close()
