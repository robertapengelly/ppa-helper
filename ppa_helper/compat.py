#------------------------------------------------------------------------------------------
#
#   Copyright 2017 Robert Pengelly.
#
#   This file is part of ppa-helper.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------------------

# coding: utf-8
from __future__ import unicode_literals

import collections
import os
import shutil
import sys

if sys.version_info >= (3, 0):
    compat_getenv = os.getenv
    compat_expanduser = os.path.expanduser

    def compat_setenv(key, value, env=os.environ):
        env[key] = value
else:
    # Environment variables should be decoded with filesystem encoding.
    # Otherwise it will fail if any non-ASCII characters present (see #3854 #3217 #2918)

    def compat_getenv(key, default=None):
        from .utils import get_filesystem_encoding
        env = os.getenv(key, default)
        if env:
            env = env.decode(get_filesystem_encoding())
        return env

# Python < 2.6.5 require kwargs to be bytes
try:
    def _testfunc(x):
        pass
    _testfunc(**{'x': 0})
except TypeError:
    def compat_kwargs(kwargs):
        return dict((bytes(k), v) for k, v in kwargs.items())
else:
    compat_kwargs = lambda kwargs: kwargs

if hasattr(shutil, 'get_terminal_size'):  # Python >= 3.3
    compat_get_terminal_size = shutil.get_terminal_size
else:
    _terminal_size = collections.namedtuple('terminal_size', ['columns', 'lines'])

    def compat_get_terminal_size(fallback=(80, 24)):
        columns = compat_getenv('COLUMNS')
        if columns:
            columns = int(columns)
        else:
            columns = None
        lines = compat_getenv('LINES')
        if lines:
            lines = int(lines)
        else:
            lines = None

        if columns is None or lines is None or columns <= 0 or lines <= 0:
            try:
                sp = subprocess.Popen(
                    ['stty', 'size'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = sp.communicate()
                _lines, _columns = map(int, out.split())
            except Exception:
                _columns, _lines = _terminal_size(*fallback)

            if columns is None or columns <= 0:
                columns = _columns
            if lines is None or lines <= 0:
                lines = _lines
        return _terminal_size(columns, lines)