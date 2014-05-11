"""
appfy.recipe.gae
================

`appfy.recipe.gae` provides a series of `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_
recipes to help with `Google App Engine <http://code.google.com/appengine/>`_
development. It is inspired by `rod.recipe.appengine <http://pypi.python.org/pypi/rod.recipe.appengine>`_,
but using a different layout and with extended functionalities. It is also
split in different recipes. Currently `appfy.recipe.gae` has 3 recipes:

:appfy.recipe.gae\:app_lib: Downloads libraries from PyPi and installs in
    the app directory.
:appfy.recipe.gae\:sdk: Downloads and installs the App Engine SDK.
:appfy.recipe.gae\:tools: Installs a python executable and several SDK
    scripts in the buildout directory: appcfg, bulkload_client, bulkloader,
    dev_appserver and remote_api_shell. It also allows to set default values
    to start the dev_appserver.

Source code and issue tracker can be found at `https://github.com/prmtl/appfy.recipe.gae <https://github.com/prmtl/appfy.recipe.gae>`_.

For an example of how appfy makes distribution of App Engine apps easy and
nice, see `Moe installation instructions <http://www.tipfy.org/wiki/moe/>`_.
"""
import os
from setuptools import setup, find_packages


def get_readme():
    base = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
    files = [
        os.path.join(base, 'README.rst'),
        os.path.join(base, 'CHANGES.txt'),
    ]
    content = []
    for filename in files:
        f = open(filename, 'r')
        content.append(f.read().strip())
        f.close()

    return '\n\n\n'.join(content)


tests_require = (
    'nose'
)


setup(
    name='appfy.recipe.gae',
    version='0.9.6',
    author='Rodrigo Moraes',
    author_email='rodrigo.moraes@gmail.com',
    maintainer='Sebastian Kalinowski',
    maintainer_email='sebastian@kalinowski.eu',
    description='Buildout recipes for App Engine development.',
    long_description=get_readme(),
    license='Apache Software License',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg >= 2.0.0'
    ],
    entry_points={
        'zc.buildout': [
            'default = appfy.recipe.gae.tools:Recipe',
            'tools = appfy.recipe.gae.tools:Recipe',
            'sdk = appfy.recipe.gae.sdk:Recipe',
            'app_lib = appfy.recipe.gae.app_lib:Recipe',
        ],
    },
    zip_safe=False,
    keywords='buildout recipe google app engine appengine gae zc.buildout '
        'appfy tipfy',
    url='https://github.com/prmtl/appfy.recipe.gae',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    test_suite='nose.collector',
)
