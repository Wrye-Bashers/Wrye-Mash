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
import imp, os, sys, types, importlib, pkgutil, traceback, modulefinder

class print_self(object):

    def __init__(self, the_self):
        print "The print_self:"
        temp_self = the_self
        print "Dir: ---"
        print dir(temp_self)
        #print "Hash: ---"
        #print hash(temp_self)
        #print "ID: ---"
        #print id(temp_self)
        print "Vars: ---"
        print vars(temp_self)
        print "Type: ---"
        print type(temp_self)
        print "Repr: ---"
        print repr(temp_self)
        #print "Keys: ---"
        #print temp_self.keys()
        print

class get_everything(object):

    def __init__(self, the_object=None, fullname=None, path=None):
        self.the_object = the_object
        self.fullname = fullname
        self.path = path

    def print_dif_keys(self, the_old_object=None, the_new_object=None):
        print "Keys: ---"
        some_keys_backup = the_old_object
        some_keys = the_new_object
        filtered_data = []
        for value in some_keys:
            if not value in some_keys_backup:
                #print "Not this one: ", value
                filtered_data.append(value)
                #filtered_data.append(value)
            #    filtered_data.append(value)
        print "The New Key(s): ", filtered_data

    def return_keys(self, the_object=None):
        print "Keys: ---"
        return the_object.keys()


    def print_all(self, the_object=None, fullname=None, path=None):
        print "The print_all:"
        print "fullname: ---"
        print (fullname)
        print "path: ---"
        print (path)
        #print "Dir: ---"
        #print dir(the_object)
        #print "Hash: ---"
        #hash(the_object)
        #print "Help: ---"
        #help(the_object)
        #print "ID: ---"
        #print id(the_object)
        #print "Vars: ---"
        #vars(the_object)
        #print "Type: ---"
        #print type(the_object)
        print "Repr: ---"
        print repr(the_object)
        #print "Importlib: ---"
        #temp_import = importlib.import_module(fullname, package=None)
        #some_keys_backup = the_object.keys()
        some_keys = the_object.keys()
        for key in range(len(some_keys)):
            print sys.modules[some_keys[key]]
        #    if hasattr(sys.modules[some_keys[key]], some_keys[key]):
        #        found = the_object[some_keys[key]].__getattr__(self, some_keys[key])
        #        print "Key: {}, Value: {}, Path: {}".format(key,some_keys[key],found)
        #some_keys.extend(['mash.gui'])
        #get_everything().print_dif_keys(the_object)
        #for key in some_keys:
        #    if hasattr(sys.modules[some_keys[key]], some_keys[key]):
        #        found = the_object[some_keys[key]].__getattr__(self, some_keys[key])
        #        print "Key: {}, Value: {}, Path: {}".format(key,some_keys[key],found)
        #if hasattr(the_object, '__dict__'):
        #    print "Vars: ---"
        #    print vars(the_object)
        #print "In Object: ---"
        #somename = 'functools'
        #if somename in the_object:
        #    print "The Object has fullname: {}".format(somename)
        #somename = 'copy_reg'
        #if somename in the_object:
        #    print "The Object has fullname: {}".format(somename)
        #found = types.ModuleType(fullname)
        #print "The module that was found with types: {}".format(found)
        #thenew = imp.new_module(fullname)
        #print "The module that was found with imp: {}".format(thenew)
        # the_found_module = the_object[fullname]
        # print "The sys.module value: {}".format(the_found_module)
        #looking_for_theloader = pkgutil.find_loader(fullname)
        #print "We are looking for the loader for fullname which was : {}".format(looking_for_theloader)

        #print vars(the_object)


class return_mod(object):

    def load_module(self, fullname):
        #code = self.get_code(fullname)
        #ispkg = self.is_package(fullname)
        mod = sys.modules.setdefault(fullname, types.ModuleType(fullname))
        crazy_thing = "<%s>" % self.__class__.__name__
        mod.__file__ = crazy_thing
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(code, mod.__dict__)
        print mod
        return mod
        print vars(fullname)

def file_exists(filename, ext, initfile):
    if os.path.exists(filename+ext):
        return True

def is_directory(full_path):
    if os.path.isdir(full_path):
        return True

def is_package(full_path, initfile, ext):
    the_initfile = os.path.join(full_path, initfile+ext)
    print the_initfile
    if os.path.exists(the_initfile):
        return True

def resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in xrange(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                              "package")
    return "%s.%s" % (package[:dot], name)


def get_module_name(fullname, path=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if fullname.startswith('.'):
        print "In get module name Path is: ", path
        level = 0
        for character in fullname:
            if character != '.':
                break
            level += 1
        fullname = resolve_name(fullname[level:], path, level)
    return fullname

class UnicodeImporter(object):
    count = 0

    @classmethod
    def set_module_path(cls,fullname=None,path=None):
        cls.prev_fullname = fullname
        cls.prev_path = path

    @classmethod
    def get_prev_path(cls, fullname):
        if cls.prev_fullname == fullname:
            return cls.prev_path


    def find_module(self,fullname,path=None):
        UnicodeImporter.set_module_path(fullname,path)
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

    def load_module(self,fullname,path=None):
        if fullname in sys.modules:
            return sys.modules[fullname]
        else: # set to avoid reimporting recursively
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
            if file_exists(filename,ext,initfile):
                with open(filename+ext,'U') as fp:
                    mod = imp.load_source(fullname,filename+ext,fp)
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
            print 'fail', filename+ext
            raise ImportError, u'caused by ' + repr(e), sys.exc_info()[2]

if not hasattr(sys,'frozen'):
    sys.meta_path = [UnicodeImporter()]

if __name__ == '__main__':
    from mash.marg import parse
    from mash.mash import main
    opts = parse()
    main(opts)