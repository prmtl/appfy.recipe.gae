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


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    This comes from Python 2.6 source.
    """
    if os.path.isfile(src):
        shutil.copyfile(src, dst)
        return

    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors


def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter.

    Patterns is a sequence of glob-style patterns
    that are used to exclude files

    This comes from Python 2.6 source.
    """
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns



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


# Imported here to avoid recursion.
#from appfy.recipe.sdk_scripts import SdkScripts
#from appfy.recipe.app_libraries import AppLibraries
#from appfy.recipe.install_sdk import InstallAppEngineSdk
