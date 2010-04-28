appfy.recipe.gae
================

`appfy.recipe.gae` provides a series of zc.buildout recipes to help App
Engine development. It is inspired by
`rod.recipe.appengine <http://pypi.python.org/pypi/rod.recipe.appengine>`_,
but with support for a more natural layout and functionalities split in
different recipes. Currently `appfy.recipe.gae` has 3 recipes:

:appfy.recipe.gae\:sdk: Downloads and installs the App Engine SDK.
:appfy.recipe.gae\:tools: Installs appcfg, dev_appserver and python
    executables.
:appfy.recipe.gae\:app_lib: Downloads packages from PyPi and installs in
    the app directory.

Source code and issue tracker can be found at `http://code.google.com/p/appfy/ <http://code.google.com/p/appfy/>`_.


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


appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory. This
recipe extends `hexagonit.recipe.download <http://pypi.python.org/pypi/hexagonit.recipe.download>`_
so all the download options from that recipe are also valid.

Options
~~~~~~~

:destination: destination of the extracted SDK download. Default is
    `${buildout:parts-directory}/google_appengine`.
:clear-destination: if `true`, deletes the destination dir before
    extracting the download. Default is `false`.

Example
~~~~~~~

::

  [gae_sdk]
  # Dowloads and extracts the App Engine SDK.
  recipe = appfy.recipe.gae:sdk
  url = http://googleappengine.googlecode.com/files/google_appengine_1.3.3.zip
  destination = ${buildout:parts-directory}/google_appengine
  strip-top-level-dir = true
  hash-name = false
  clear-destination = true


appfy.recipe.gae:tools
----------------------

Installs appcfg, dev_appserver and python executables in the buildout
directory. It also allows to set default values to start the dev_appserver.

This recipe extends `zc.recipe.egg <http://pypi.python.org/pypi/zc.recipe.egg>`_
so all the options from that recipe are also valid.

Options
~~~~~~~

:sdk-directory: path to the App Engine SDK directory. It can be an
    absolute path or a reference to the `appfy.recipe.gae:sdk` destination
    option. Default is `${buildout:parts-directory}/google_appengine`.
:dev_appserver-script: path to the dev_appserver script. Default is
    `${buildout:bin-directory}/dev_appserver`.
:appcfg-script: path to the appcfg script. Default is
    `${buildout:bin-directory}/appcfg`.


Example
~~~~~~~

::

  [gae_tools]
  # Installs appcfg, dev_appserver and python executables in the bin directory.
  recipe = appfy.recipe.gae:tools
  sdk-directory = ${gae_sdk:destination}


Note that this example references an `gae_sdk` section from the
`appfy.recipe.gae:sdk` example. An absolute path could also be used.

To set default values to start the dev_appserver, create a section
`dev_appserver` in buildout.cfg. For example:

::

  [dev_appserver]
  # Set default values to start the dev_appserver. All options from the
  # command line are allowed. They are inserted at the beginning of the
  # arguments. Values are used as they are; don't use variables here.
  defaults = --datastore_path=var --history_path=var --blobstore_path=var app


These options can be set in a single line as well. If an option is provided
when calling dev_appserver, it will override the default value if it is set.