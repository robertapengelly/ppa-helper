#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os.path
import warnings
import sys

try:
    from setuptools import setup, Command
    setuptools_available = True
except ImportError:
    from distutils.core import setup, Command
    setuptools_available = False
from distutils.spawn import spawn

try:
    # This will create an exe that needs Microsoft Visual C++ 2008
    # Redistributable Package
    import py2exe
except ImportError:
    if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
        print('Cannot import py2exe', file=sys.stderr)
        exit(1)

py2exe_options = {
    'bundle_files': 1,
    'compressed': 1,
    'optimize': 2,
    'dist_dir': '.'
}

__version__ = '2017.10.07'

DESCRIPTION = 'PPA Helper'
LONG_DESCRIPTION = 'A program designed to make adding ppa source\'s easier.'

py2exe_console = [{
    'script': './__main__.py',
    'dest_base': 'ppa-helper',
    'version': __version__,
    'description': DESCRIPTION,
    'comments': LONG_DESCRIPTION,
    'product_name': 'ppa-helper',
    'product_version': __version__,
}]

py2exe_params = {
    'console': py2exe_console,
    'options': {'py2exe': py2exe_options},
    'zipfile': None
}

if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    params = py2exe_params
else:
    params = {}
    
    if setuptools_available:
        params['entry_points'] = {'console_scripts': ['ppa-helper = ppa_helper:main']}
    else:
        params['scripts'] = ['bin/ppa-helper']

setup(
    name='ppa_helper',
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/robertapengelly/ppa-helper',
    author='Robert Pengelly',
    author_email='robertapengelly@hotmail.co.uk',
    maintainer='Robert Pengelly.',
    maintainer_email='robertapengelly@hotmail.co.uk',
    packages=['ppa_helper'],

    # Provokes warning on most systems (why?!)
    # test_suite = 'nose.collector',
    # test_requires = ['nosetest'],

    classifiers=[
        'Topic :: Multimedia :: Video',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: Public Domain',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    **params
)