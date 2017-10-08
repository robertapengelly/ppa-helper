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

#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import optparse
import os
import re
import subprocess
import sys
import time
import urllib

from .compat import (
    compat_get_terminal_size,
    compat_kwargs
)

from .utils import preferredencoding

__version__ = '2017.10.07'

codenames = ['warty', 'hoary', 'breezy', 'dapper', 'edgy', 'feisty', 'gutsy', 'hardy', 'intrepid', 'jaunty',
             'karmic', 'lucid', 'maverick', 'natty', 'oneiric', 'precise', 'quantal', 'raring', 'saucy', 'trusty',
             'utopic', 'vivid', 'wily', 'xenial', 'yakkety', 'zesty', 'artful']

def add_ppas(codename, ppas):
    for i in range(0, len(codenames), 1):
        if codenames[i] == codename:
            break
    
    start = i
    
    for ppa in ppas:
        distro = codename
        match = re.match('ppa[^:]*:([^"]+)', ppa)
        
        if match:
            ppa = match.group(1)
        
        url = 'http://ppa.launchpad.net/' + ppa + '/ubuntu/dists/'
        result = urllib.urlopen(url);
        
        if not result.getcode() == 200:
            print 'We are unable to find', ppa
            time.sleep(5)
            continue;
        
        data = result.read();
        exists = re.search('<a href="' + distro + '/">' + distro + '/</a>', data)
        
        if not exists:
            for i in range(start - 1, -1, -1):
                distro = codenames[i]
                exists = re.search('<a href="' + distro + '/">' + distro + '/</a>', data)
                
                if exists:
                    break
        
        if not exists:
            print 'We couldn\'t find a compatible version for', ppa, 'so the ppa will not be added'
            time.sleep(5)
            continue
        
        deb = 'deb http://ppa.launchpad.net/' + ppa + '/ubuntu ' + distro + ' main'
        deb_src = '# deb-src http://ppa.launchpad.net/' + ppa + '/ubuntu ' + distro + ' main'
        
        args = re.match('([^"]+)/([^"]+)', ppa);
        os.system('echo \'' + deb + '\\n' + deb_src + '\' | sudo tee /etc/apt/sources.list.d/' + args.group(1) + '-ubuntu-' + args.group(2) + '-' + distro + '.list > /dev/null')
        
        url = 'https://launchpad.net/~' + args.group(1) + '/+archive/ubuntu/' + args.group(2)
        result = urllib.urlopen(url);
        
        if not result.getcode() == 200:
            print 'We are unable to get the signing key for', ppa
            time.sleep(5)
            continue;
        
        data = result.read();
        fingerprint = re.search('<dt>Fingerprint[^:]*:</dt>[^"]+<dd>([^"]+)</dd>', data)
        fingerprint = fingerprint.group(1)
        
        os.system('sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ' + fingerprint)

def parseOpts(overrideArguments=None):
    def _format_option_string(option):
        opts = []
        
        if option._short_opts:
            opts.append(option._short_opts[0])
        
        if option._long_opts:
            opts.append(option._long_opts[0])
        
        if len(opts) > 1:
            opts.insert(1, ', ')
        
        if option.takes_value():
            opts.append(' %s' % option.metavar)
        
        return ''.join(opts)
    
    def compat_conf(conf):
        if sys.version_info < (3,):
            return [a.decode(preferredencoding(), 'replace') for a in conf]
        return conf
    
    def optional_arg(arg_default):
        def func(option, opt_str, value,parser):
            if parser.rargs and not parser.rargs[0].startswith('-'):
                val = parser.rargs[0]
                parser.rargs.pop(0)
            else:
                val = arg_default
            
            setattr(parser.values, option.dest, val)
        
        return func
    
    # No need to wrap help messages if we're on a wide console
    columns = compat_get_terminal_size().columns
    max_width = columns if columns else 80
    max_help_position = 80
    
    fmt = optparse.IndentedHelpFormatter(width=max_width, max_help_position=max_help_position)
    fmt.format_option_strings = _format_option_string
    
    kw = {
        'version': __version__,
        'formatter': fmt,
        'conflict_handler': 'resolve',
    }
    
    parser = optparse.OptionParser(**compat_kwargs(kw))
    
    action = optparse.OptionGroup(parser, 'Action Options')
    action.add_option(
        '-a', '--add',
        action='callback',
        callback=optional_arg('empty'),
        dest='add',
        help='Adds the provided ppa or ppa\'s to sources.list.d.'
    )
    action.add_option(
        '-u', '--update',
        action='callback',
        callback=optional_arg('all'),
        dest='update',
        help='Updates all existing ppa\'s in sources.list.d or updates the provided ppa or ppa\'s (if any provided).'
    )
    
    parser.add_option_group(action)
    
    command_line_conf = compat_conf(sys.argv[1:])
    opts, args = parser.parse_args(command_line_conf)
    
    return parser, opts, args

def update_ppas(codename, ppas):
    if ppas[0] == 'all':
        update_sources(codename)
    else:
        for ppa in ppas:
            update_source(codename, ppa)

def update_source(codename, ppa):
    sources = [f for f in os.listdir('/etc/apt/sources.list.d') if os.path.isfile(os.path.join('/etc/apt/sources.list.d', f))]
    
    for source in sources:
        contents = subprocess.check_output(['cat', '/etc/apt/sources.list.d/' + source])
        match = re.match('[^"]+ ([^"]+/' + ppa + '/ubuntu) ([^"]+) main', contents)
        
        if match:
            break
    
    if match and not match.group(2) == codename:
        curr_distro = match.group(2)
        
        for i in range(0, len(codenames), 1):
            if codenames[i] == codename:
                break

        start = i
        
        distro = codename
        url = match.group(1) + '/dists/'
        result = urllib.urlopen(url);
        
        if not result.getcode() == 200:
            print 'We are unable to find', ppa
            time.sleep(5)
            return;
        
        data = result.read();
        exists = re.search('<a href="' + distro + '/">' + distro + '/</a>', data)
        
        if not exists:
            for i in range(start - 1, -1, -1):
                distro = codenames[i]
                exists = re.search('<a href="' + distro + '/">' + distro + '/</a>', data)
                
                if exists:
                    break
        
        if not exists:
            print 'We couldn\'t find a compatible version for', ppa, 'so the ppa will not be added'
            time.sleep(5)
            return
        
        deb = 'deb ' + match.group(1) + ' ' + distro + ' main'
        deb_src = '# deb-src ' + match.group(1) + ' ' + distro + ' main'
        
        os.system('echo \'' + deb + '\\n' + deb_src + '\' | sudo tee /etc/apt/sources.list.d/' + source + ' > /dev/null')
        
        match = re.match('([^"]+)' + curr_distro + '([^"]+)', source)
        
        if not match:
            return
        
        os.system('sudo mv -vi /etc/apt/sources.list.d/' + source + ' /etc/apt/sources.list.d/' + match.group(1) + distro + match.group(2))

def update_sources(codename):
    sources = [f for f in os.listdir('/etc/apt/sources.list.d') if os.path.isfile(os.path.join('/etc/apt/sources.list.d', f))]
    
    for source in sources:
        contents = subprocess.check_output(['cat', '/etc/apt/sources.list.d/' + source])
        contents = re.split('\\n', contents);
        
        for line in contents:
            match = re.match('[^"]+ http[^s?]*s?://ppa.launchpad.net/[^"]+/ubuntu ([^"]+) main', line)
            
            if match:
                break;
        
        if not match or match.group(1) == codename:
            continue
        
        curr_distro = match.group(1)
        match = re.match('[^"]+ ([^"]+) ' + curr_distro + ' main', line)
        
        if not match:
            continue
        
        for i in range(0, len(codenames), 1):
            if codenames[i] == codename:
                break

        start = i
        
        distro = codename
        url = match.group(1) + '/dists/'
        result = urllib.urlopen(url);
        
        if not result.getcode() == 200:
            print 'We are unable to find', ppa
            time.sleep(5)
            continue;
        
        data = result.read();
        exists = re.search('<a href="' + distro + '/">' + distro + '/</a>', data)
        
        if not exists:
            for i in range(start - 1, -1, -1):
                distro = codenames[i]
                exists = re.search('<a href="' + distro + '/">' + distro + '/</a>', data)
                
                if exists:
                    break
        
        if not exists:
            print 'We couldn\'t find a compatible version for', ppa, 'so the ppa will not be added'
            time.sleep(5)
            continue
        
        deb = 'deb ' + match.group(1) + ' ' + distro + ' main'
        deb_src = '# deb-src ' + match.group(1) + ' ' + distro + ' main'
        
        os.system('echo \'' + deb + '\\n' + deb_src + '\' | sudo tee /etc/apt/sources.list.d/' + source + ' > /dev/null')
        
        match = re.match('([^"]+)' + curr_distro + '([^"]+)', source)
        
        if not match:
            continue
        
        os.system('sudo mv -vi /etc/apt/sources.list.d/' + source + ' /etc/apt/sources.list.d/' + match.group(1) + distro + match.group(2))

def main(argv=None):
    codename = re.match('Codename[^:]*:\s([^"]+)\\n', subprocess.check_output(['lsb_release', '--codename']))
    
    if not codename:
        print 'You are using an unsupported distro.'
        sys.exit(0)
    
    codename = codename.group(1)
    parser, opts, args = parseOpts(argv)
    
    add = None
    update = None
    
    for opt in vars(opts):
        if opt == 'add' and getattr(opts, opt):
            add = re.split(' +', getattr(opts, opt))
        elif opt == 'update' and getattr(opts, opt):
            update = re.split(' +', getattr(opts, opt))
    
    if add:
        if add[0] == 'empty':
            parser.print_help()
            sys.exit(0)
        
        add_ppas(codename, add)
    
    if update:
        update_ppas(codename, update)
    
    os.system('sudo apt-get update')