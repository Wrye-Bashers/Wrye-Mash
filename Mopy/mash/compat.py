# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Mash.
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# =============================================================================
'''
Mash uses cPickle to store data. This means that whenever the code changes
much then it breaks backwards compatiblity. The sane solution would be to
convert everything to use json. However for my sanity, this file
provides a workaround to enable the renaming of files


(This is not a nice solution)
'''

import sys
import cPickle


def findClass(module, name):
    '''
    Find class implementation. The same as pickle.Unpickler.find_class but
    translates module names
    '''
    if module in (
        'balt', 
        'bolt',
        'conf',
        'env',
        'errorlog',
        'exception',
        'localization',
        'marg',
        'mash', 
        'masher', 
        'mosh', 
        'mush', 
        'mysh'
        ):
        module = 'mash.' + module

    if module in (
        '__init__', 
        'dialog',
        'helpbrowser',
        # 'screens', because it's empty
        'settings',
        'utils',
        ):
        module = 'mash.gui.' + module

    if module in (
        'fakemlox', 
        'loader',
        ):
        module = 'mash.mlox.' + module

    if module in (
        '__init__', 
        'gui',
        'tes3cmdgui',
        ):
        module = 'mash.tes3cmd.' + module

    __import__(module)
    mod = sys.modules[module]
    klass = getattr(mod, name)
    return klass


def uncpickle(f):
    '''
    Same as cPickle.loads(f) but does module name translation
    '''
    pickleObj = cPickle.Unpickler(f)
    pickleObj.find_global = findClass
    return pickleObj.load()
