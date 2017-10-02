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
import cPickle
import os
import fnmatch
import imp


def findMlox(start):
    """
    Attempts to find mlox in the give path. It avoids serching Data Files
    """
    for root, dirnames, filenames in os.walk(start):
        try:
            dirnames.remove('Data Files')
        except ValueError:
            pass
        try:
            dirnames.remove('Installers')
        except ValueError:
            pass

        for filename in fnmatch.filter(filenames, 'mlox.py'):
            return root
    return None


def mloxFromCfg():
    try:
        pk = open('startup.settings.pkl', 'rb');
        mloxPath = cPickle.load(pk)
        pk.close()
        if os.path.exists(os.path.join(mloxPath, 'mlox.py')):
            return mloxPath
    except (IOError, EOFError):
        pass
    return None


def saveMloxCfg(path):
    pk = open('startup.settings.pkl', 'wb');
    mloxPath = cPickle.dump(path, pk)
    pk.close()


def importMlox():
    wd = os.getcwd()
    mloxPath = mloxFromCfg() or findMlox(os.path.dirname(wd))

    if mloxPath:
        # ugly hack to get around some mlox data loading issues
        os.chdir(mloxPath)
        mlox = imp.load_source('mlox', os.path.join(mloxPath, 'mlox.py'))
        os.chdir(wd)

        saveMloxCfg(mloxPath)
        return mlox
    else:
        from . import fakemlox
        return fakemlox
