#!/usr/bin/env python2
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
import os, sys, types, importlib

class UnicodeImporter(object):
    def find_module(self,fullname,path=None):
        print(fullname)
        arg1, arg2, arg3 = types.ModuleType(fullname)
        print(arg1, arg2, arg3)

        for name in sys.modules:
            print (name)
            if name == fullname and name in sys.modules:
                print (fullname)
                print (sys.modules[fullname])
                print ("Found fullname: {}".format(fullname))
            else:
                print ("Name {} not equal to fullname: {}".format(name, fullname))

        if isinstance(fullname,unicode):
            fullname = fullname.replace(u'.',u'\\')
            exts = (u'.pyc',u'.pyo',u'.py')
        else:
            fullname = fullname.replace('.','\\')
            exts = ('.pyc','.pyo','.py')
        if os.path.exists(fullname) and os.path.isdir(fullname):
            return self
        for ext in exts:
            if os.path.exists(fullname+ext):
                return self

    def load_module(self,fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        else: # set to avoid reimporting recursively
            types_imp = types.ModuleType(fullname)
            importlib_imp = importlib.import_module(fullname)
            sys.modules[fullname] = types.ModuleType(fullname)

        if isinstance(fullname,unicode):
            filename = fullname.replace(u'.',u'\\')
            ext = u'.py'
            initfile = u'__init__'
        else:
            filename = fullname.replace('.','\\')
            ext = '.py'
            initfile = '__init__'
        try:
            if os.path.exists(filename+ext):
                with open(filename+ext,'U') as fp:
                    mod = importlib.import_module(fullname)
                    sys.modules[fullname] = mod
                    mod.__loader__ = self
            else:
                mod = sys.modules[fullname]
                mod.__loader__ = self
                mod.__file__ = os.path.join(os.getcwd(),filename)
                mod.__path__ = [filename]
                #init file
                initfile = os.path.join(filename,initfile+ext)
                if os.path.exists(initfile):
                    with open(initfile,'U') as fp:
                        code = fp.read()
                    exec compile(code, initfile, 'exec') in mod.__dict__
            return mod
        except Exception as e: # wrap in ImportError a la python2 - will keep
            # the original traceback even if import errors nest
            print('fail', filename+ext)
            raise ImportError(u'caused by ' + repr(e), sys.exc_info()[2])

if not hasattr(sys,'frozen'):
    sys.meta_path = [UnicodeImporter()]

if __name__ == '__main__':
    from mash.marg import parse
    from mash.mash import main
    opts = parse()
    main(opts)