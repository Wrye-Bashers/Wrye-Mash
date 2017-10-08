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
from os.path import join as jo

import conf

opts = None # command line arguments used when launching Bash, set on bash

def init_settings_files():
    """Construct a dict mapping directory paths to setting files. Keys are
    tuples of absolute paths to directories, paired with the relative paths
    in the backup file. Values are sets of setting files in those paths,
    or empty, meaning we have to list those paths and backup everything."""
    dirs = conf.dirs
    game = 'mw'
    settings_info = {
        (dirs['mopy'], jo(game, u'Mopy')): {u'bash.ini', },
        (dirs['mods'].join(u'Bash'), jo(game, u'Data', u'Bash')): {
            u'Table.dat', },
        (dirs['mods'].join(u'Docs'), jo(game, u'Data', u'Docs')): {
            u'Bash Readme Template.txt', u'Bash Readme Template.html',
            u'My Readme Template.txt', u'My Readme Template.html',
            u'wtxt_sand_small.css', u'wtxt_teal.css', },
        (dirs['modsBash'], jo(game + u' Mods', u'Bash Mod Data')): {
            u'Table.dat', },
        (dirs['modsBash'].join(u'INI Data'),
         jo(game + u' Mods', u'Bash Mod Data', u'INI Data')): {
           u'Table.dat', },
        (dirs['bainData'], jo(game + u' Mods', u'Bash Installers', u'Bash')): {
           u'Converters.dat', u'Installers.dat', },
        (dirs['saveBase'], jo(u'My Games', game)): {
            u'BashProfiles.dat', u'BashSettings.dat', u'BashLoadOrders.dat',
            u'People.dat', },
        # backup all files in Mopy\bash\l10n, Data\Bash Patches\ and
        # Data\INI Tweaks\
        (dirs['l10n'], jo(game, u'Mopy', u'bash', u'l10n')): {},
        (dirs['mods'].join(u'Bash Patches'),
         jo(game, u'Data', u'Bash Patches')): {},
        (dirs['mods'].join(u'INI Tweaks'),
         jo(game, u'Data', u'INI Tweaks')): {},
    }
    #for setting_files in settings_info.itervalues():
    #    for name in set(setting_files):
    #        if name.endswith(u'.dat'): # add corresponding bak file
    #            setting_files.add(name[:-3] + u'bak')
    #return settings_info

def SameAppVersion():
    return not cmp(conf.app_version, conf.settings['mash.version'])

#TODO: Add the cPickle routines for reading settings files to here
