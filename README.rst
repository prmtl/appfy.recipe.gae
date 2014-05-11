appfy.recipe.gae
================

.. image:: https://travis-ci.org/prmtl/appfy.recipe.gae.png?branch=master
   :target: https://travis-ci.org/prmtl/appfy.recipe.gae

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
:ignore-packages: A list of top-level package names or modules to be ignored.
    This is useful to ignore dependencies that won't be used. Some packages may
    install distribute, setuptools or pkg_resources but these are not very
    useful on App Engine, so you can set them to be ignored, for example.
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

  # Don't install these packages or modules.
  ignore-packages =
      distribute
      setuptools
      easy_install
      site
      pkg_resources


appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory.

Options
~~~~~~~

:url: URL to the App Engine SDK file.
:destination: Destination of the extracted SDK. Default is the parts directory.
:clear-destination: If `true`, deletes the destination dir before
    extracting the download. Default is `true`.

Example
~~~~~~~

::

  [gae_sdk]
  # Dowloads and extracts the App Engine SDK.
  recipe = appfy.recipe.gae:sdk
  url = http://googleappengine.googlecode.com/files/google_appengine_1.3.5.zip
  destination = ${buildout:parts-directory}
  hash-name = false
  clear-destination = true


appfy.recipe.gae:tools
----------------------

Installs a python executable and several SDK scripts in the buildout
directory: appcfg, bulkload_client, bulkloader, dev_appserver and
remote_api_shell.

It also allows to set default values to start the dev_appserver.

This recipe extends `zc.recipe.egg.Scripts <http://pypi.python.org/pypi/zc.recipe.egg>`_,
so all the options from that recipe are also valid.

Options
~~~~~~~

:sdk-directory: Path to the App Engine SDK directory. It can be an
    absolute path or a reference to the `appfy.recipe.gae:sdk` destination
    option. Default is `${buildout:parts-directory}/google_appengine`.
:appcfg-script: Name of the appcfg script to be installed in the bin
    directory.. Default is `appcfg`.
:bulkload_client-script: Name of the bulkloader script to be installed in
    the bin directory. Default is `bulkload_client`.
:bulkloader-script: Name of the bulkloader script to be installed in
    the bin directory. Default is `bulkloader`.
:dev_appserver-script: Name of the dev_appserver script to be installed in
    the bin directory. Default is `dev_appserver`.
:remote_api_shell-script: Name of the remote_api_shell script to be
    installed in the bin directory. Default is `remote_api_shell`.
:config-file: Configuration file with the default values to use in
    scripts. Default is `gaetools.cfg`.
:extra-paths: Extra paths to include in sys.path for generated scripts.
:initialization: Allows to specify some Python code to be included in
    the scripts.

Example
~~~~~~~

::

  [gae_tools]
  # Installs appcfg, dev_appserver and python executables in the bin directory.
  recipe = appfy.recipe.gae:tools
  sdk-directory = ${gae_sdk:destination}/google_appengine
  # add extra code
  initialization =
    import dev_appserver
    dev_appserver.fix_sys_path()
  # Add these paths to sys.path in the generated scripts.
  extra-paths =
      app/lib
      app/distlib

Note that this example references an `gae_sdk` section from the
`appfy.recipe.gae:sdk` example. An absolute path could also be used.

To set default values to start the dev_appserver, create a section
`dev_appserver` in the defined configuration file (`gaetools.cfg` by
default). For example::

  [dev_appserver]
  # Set default values to start the dev_appserver. All options from the
  # command line are allowed. They are inserted at the beginning of the
  # arguments. Values are used as they are; don't use variables here.
  recipe = appfy.recipe.gae:tools
  defaults =
      --datastore_path=var/data.store
      --history_path=var/history.store
      --blobstore_path=var/blob.store
      app


Each option should be set in a separate line, as displayed above. Options
provided when calling dev_appserver will override the default values.
