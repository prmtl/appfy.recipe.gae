"""
appfy.recipe.gae
================

`appfy.recipe.gae` provides a series of zc.buildout recipes to help App
Engine development. It is inspired by
`rod.recipe.appengine <http://pypi.python.org/pypi/rod.recipe.appengine>`_,
but using a different layout and with extended functionalities. It is also
split in different recipes. Currently `appfy.recipe.gae` has 3 recipes:

:appfy.recipe.gae\:sdk: Downloads and installs the App Engine SDK.
:appfy.recipe.gae\:tools: Installs a python executable and several SDK
    scripts in the buildout directory: appcfg, bulkload_client, bulkloader,
    dev_appserver and remote_api_shell. It also allows to set default values
    to start the dev_appserver.
:appfy.recipe.gae\:app_lib: Downloads libraries from PyPi and installs in
    the app directory.

Source code and issue tracker can be found at `http://code.google.com/p/appfy/ <http://code.google.com/p/appfy/>`_.
"""
import os
from setuptools import setup, find_packages


def get_readme():
    base = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
    files = [
        os.path.join(base, 'README.txt'),
        os.path.join(base, 'CHANGES.txt'),
    ]
    content = []
    for filename in files:
        f = open(filename, 'r')
        content.append(f.read().strip())
        f.close()

    return '\n\n\n'.join(content)


setup(
    name='appfy.recipe.gae',
    version='0.2',
    author='Rodrigo Moraes',
    author_email='rodrigo.moraes@gmail.com',
    description='Buildout recipes for App Engine development.',
    long_description=get_readme(),
    license='Apache Software License',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'zc.buildout >= 1.4.3',
        'zc.recipe.egg >= 1.2.2',
        'hexagonit.recipe.download >= 1.4.1',
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
    url='http://code.google.com/p/appfy/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
