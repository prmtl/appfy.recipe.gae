"""
appfy
=====


"""
from setuptools import setup, find_packages

setup(
    name='appfy',
    version='0.1',
    author='Rodrigo Moraes',
    author_email='rodrigo.moraes@gmail.com',
    description='Buildout recipes for App Engine development.',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'setuptools >= 0.6c11',
        'zc.buildout >= 1.4.3',
        'zc.recipe.egg >= 1.2.2',
        'hexagonit.recipe.download >= 1.4.1',
    ],
    entry_points={
        'zc.buildout': [
            'default = appfy.recipe.gae_tools:Recipe',
            'gae_tools = appfy.recipe.gae_tools:Recipe',
            'gae_sdk = appfy.recipe.gae_sdk:Recipe',
            'app_libs = appfy.recipe.app_libs:Recipe',
        ],
    },
    zip_safe=False,
    keywords='buildout recipe google app engine appengine gae zc.buildout tipfy',
    url='http://pypi.python.org/pypi/appfy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
