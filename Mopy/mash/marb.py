# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2015 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================
import ConfigParser
import os
import sys
#from os.path import join as jo

import wx

import conf
from bolt import GPath, Path

from localization import _, formatInteger, formatDate

opts = None # command line arguments used when launching Bash, set on bash

def init_settings_files():
    dirs = conf.dirs
    mwDir = conf.settingDefaults['mwDir']
    parentDir = os.path.split(os.getcwd())[0]
    #settings_info = {
    #    (conf.dirs['mopy'], jo(game, u'Mopy')): {u'bash.ini', },
    #    (conf.dirs['mods'].join(u'Bash'), jo(game, u'Data', u'Bash')): {
    #        u'Table.dat', },
    #    (conf.dirs['mods'].join(u'Docs'), jo(game, u'Data', u'Docs')): {
    #        u'Bash Readme Template.txt', u'Bash Readme Template.html',
    #        u'My Readme Template.txt', u'My Readme Template.html',
    #        u'wtxt_sand_small.css', u'wtxt_teal.css', },
    #    (conf.dirs['modsBash'], jo(game + u' Mods', u'Bash Mod Data')): {
    #        u'Table.dat', },
    #    (conf.dirs['modsBash'].join(u'INI Data'),
    #     jo(game + u' Mods', u'Bash Mod Data', u'INI Data')): {
    #       u'Table.dat', },
    #    (conf.dirs['bainData'], jo(game + u' Mods', u'Bash Installers', u'Bash')): {
    #       u'Converters.dat', u'Installers.dat', },
    #    (conf.dirs['saveBase'], jo(u'My Games', game)): {
    #        u'BashProfiles.dat', u'BashSettings.dat', u'BashLoadOrders.dat',
    #        u'People.dat', },
    #    # backup all files in Mopy\bash\l10n, Data\Bash Patches\ and
    #    # Data\INI Tweaks\
    #    (conf.dirs['l10n'], jo(game, u'Mopy', u'bash', u'l10n')): {},
    #    (conf.dirs['mods'].join(u'Bash Patches'),
    #     jo(game, u'Data', u'Bash Patches')): {},
    #    (conf.dirs['mods'].join(u'INI Tweaks'),
    #     jo(game, u'Data', u'INI Tweaks')): {},
    #}
    #for setting_files in settings_info.itervalues():
    #    for name in set(setting_files):
    #        if name.endswith(u'.dat'): # add corresponding bak file
    #            setting_files.add(name[:-3] + u'bak')
    #return settings_info

def SameAppVersion():
    return not cmp(conf.app_version, conf.settings['mash.version'])

#TODO: Add the cPickle routines for reading settings files to here

def BrowseToMWDir():
    """Dialog to select Morrowind installation directory. Called by OnInit()."""
    # --Ask user through dialog.
    while True:
        mwDirDialog = wx.DirDialog(None,
            _(u"Select your Morrowind installation directory."))
        result = mwDirDialog.ShowModal()
        mwDir = mwDirDialog.GetPath()
        mwDirDialog.Destroy()
        # --User canceled?
        if result != wx.ID_OK:
            return False
        # --Valid Morrowind install directory?
        elif os.path.exists(os.path.join(mwDir, u'Morrowind.ini')):
            conf.settings['mwDir'] = mwDir
            conf.dirs['app'] = GPath(mwDir)
            return True
        # --Retry?
        retryDialog = wx.MessageDialog(None, _(
            u"Can't find Morrowind.ini in {!s}! Try again?".format(mwDir)),
            _(u'Morrowind Install Directory'),
            wx.YES_NO | wx.ICON_EXCLAMATION)
        result = retryDialog.ShowModal()
        retryDialog.Destroy()
        if result != wx.ID_YES:
            return False

# These correspond to the directories below
# "mosh.modInfos.objectMaps" : None,
# "mosh.fileInfo.backupDir"  : None,
# "mosh.fileInfo.hiddenDir"  : None,
# "mosh.fileInfo.snapshotDir": None,
_defaultDirectoryExtensions = {
    'objectMaps'      : r'Mash\ObjectMaps.pkl',
    'backupDir'       : r'Mash\Backups',
    'hiddenDir'       : r'Mash\Hidden',
    'snapshotDir'     : r'Mash\Snapshots',
    'officialLocalCSV': r'Mash\Official_Local.csv',

    'morrowindMods'   : r'Morrowind Mods',
    'mashInstallers'  : r'Morrowind Mods\Mash Installers',
    'InstallersData'  : r'Morrowind Mods\Installers Data',
}

# Have we already found the morrowind.ini file
#if os.path.exists(os.path.join(conf.settings['mwDir'], u'Morrowind.ini')):
#    return
# --Try parent directory.
#parentDir = os.path.split(os.getcwd())[0]
#if os.path.exists(os.path.join(parentDir, u'Morrowind.ini')):
#    conf.settings['mwDir'] = parentDir
#    conf.dirs['app'] = GPath(parentDir)
#    return
#def getDataDir():
#    cwd = os.getcwd()
#    mwdir = os.path.dirname(cwd)
#    return os.path.join(mwdir, 'Data Files')

def initDirs():
    """Init directories. Assume that settings has already been initialized."""
    # --Bash Ini
    mashIni = None
    if not conf.settings['mwDir']:
        conf.settings['mopyDir'] = os.getcwd()
        parentDir = os.path.split(conf.settings['mopyDir'])[0]
        conf.settings['mwDir'] = parentDir
    else:
        parentDir = conf.settings['mwDir']
        conf.settings['mopyDir'] = os.getcwd()

    if not GPath(Path(parentDir).join('Morrowind.exe').s).exists():
        BrowseToMWDir()
    # These are now defined
    # conf.settings['mwDir'] will be a string where the EXE is located
    # conf.dirs['app'] will be a path to where the EXE is located
    # mwDirParent is intended to be the parent of Morrowind where Morrowind.exe
    # is located. For example G:\Games\steamapps\common\Morrowind contains the
    # Morrowind.exe so the parent is G:\Games\steamapps\common
    # This parent directory is used as the prefix for other directories
    # such as the installers
    if not conf.settings['mwDirParent']:
        conf.settings['mwDirParent'] = conf.settings['mwDir'].split('\\Morrowind')[0]



    if GPath('mash.ini').exists():
        mashIni = ConfigParser.ConfigParser()
        mashIni.read('mash.ini')
    # --Installers
    if mashIni and mashIni.has_option('General', 'sInstallersDir'):
        conf.dirs['installers'] = GPath(mashIni.get('General', 'sInstallersDir').strip())
        conf.settings['sInstallersDir'] = conf.dirs['installers'].s
    else:
        conf.settings['sInstallersDir'] = Path(conf.settings['mwDirParent']).join(_defaultDirectoryExtensions['mashInstallers']).s
        conf.dirs['installers'] = GPath(conf.settings['sInstallersDir'])
    # --Installers Data
    if mashIni and mashIni.has_option('General', 'sInstallersData'):
        conf.dirs['installersData'] = GPath(mashIni.get('General', 'sInstallersData').strip())
        conf.settings['installersData'] = conf.dirs['installersData'].s
    else:
        conf.settings['installersData'] = Path(conf.settings['mwDirParent']).join(_defaultDirectoryExtensions['InstallersData']).s
        conf.dirs['installersData'] = GPath(conf.settings['installersData'])
    # --Morrowind
    if mashIni and mashIni.has_option('General', 'sMorrowindPath'):
        conf.dirs['app'] = GPath(mashIni.get('General', 'sMorrowindPath').strip())
        conf.settings['mwDir'] = conf.dirs['app'].s

    conf.settings['mosh.modInfos.objectMaps'] = _defaultDirectoryExtensions['objectMaps']
    conf.settings['mosh.fileInfo.backupDir'] = _defaultDirectoryExtensions['backupDir']
    conf.settings['mosh.fileInfo.hiddenDir'] = _defaultDirectoryExtensions['hiddenDir']
    conf.settings['mosh.fileInfo.snapshotDir'] = _defaultDirectoryExtensions['snapshotDir']
    conf.settings['mosh.InstallersData.officialLocalCSV'] = _defaultDirectoryExtensions['officialLocalCSV']

    if not conf.settings['mloxDir']:
        conf.settings['mloxDir'] = conf.settings['mwDir'] + '\\Mopy\\mlox'
        if GPath(conf.settings['mloxDir']).exists():
             conf.dirs['mloxDir'] = GPath(conf.settings['mloxDir'])

    # Set System Directories
    # conf.dirs['app'] is where Morrowind.exe is located
    # conf.dirs['mods'] should resolve to folder relative to the EXE
    conf.dirs['app'] = GPath(conf.settings['mwDir'])
    conf.dirs['mods'] = conf.dirs['app'].join('Data Files')
    # Detect Windows and make installers folder if it doesn't exist
    if sys.platform.lower().startswith("win") == True:
        drv, pth = os.path.splitdrive(conf.dirs['installers'].s)
        if os.access(drv, os.R_OK):
            # -# Testing the directories
            # class Dummy: chk = None

            # def testDir(a, d, ds):
            # if d in dirs['installers'].s:
            # Dummy.chk = os.access(d, a)

            # os.path.walk(dirs['installers'].s, testDir, os.F_OK)
            # print "chk", Dummy.chk
            # -#
            # print "Installers directory found."
            conf.dirs['installers'].makedirs()
        drv, pth = os.path.splitdrive(conf.dirs['installersData'].s)
        if os.access(drv, os.R_OK):
            conf.dirs['installersData'].makedirs()
