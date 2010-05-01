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


appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory. This
recipe extends `hexagonit.recipe.download <http://pypi.python.org/pypi/hexagonit.recipe.download>`_
so all the download options from that recipe are also valid.

Options
~~~~~~~

:destination: Destination of the extracted SDK download. Default is
    `${buildout:parts-directory}/google_appengine`.
:clear-destination: If `true`, deletes the destination dir before
    extracting the download. Default is `false`.

Example
~~~~~~~

::

  [gae_sdk]
  # Dowloads and extracts the App Engine SDK.
  recipe = appfy.recipe.gae:sdk
  url = http://googleappengine.googlecode.com/files/google_appengine_1.3.3.zip
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

Example
~~~~~~~

::

  [gae_tools]
  # Installs appcfg, dev_appserver and python executables in the bin directory.
  recipe = appfy.recipe.gae:tools
  sdk-directory = ${gae_sdk:destination}/google_appengine


Note that this example references an `gae_sdk` section from the
`appfy.recipe.gae:sdk` example. An absolute path could also be used.

To set default values to start the dev_appserver, create a section
`dev_appserver` in the defined configuration file (`gaetools.cfg` by
default). For example::

  [dev_appserver]
  # Set default values to start the dev_appserver. All options from the
  # command line are allowed. They are inserted at the beginning of the
  # arguments. Values are used as they are; don't use variables here.
  defaults =
      --datastore_path=var/data.store
      --history_path=var/history.store
      --blobstore_path=var/blob.store
      app


Each option should be set in a separate line, as displayed above. Options
provided when calling dev_appserver will override the default values.