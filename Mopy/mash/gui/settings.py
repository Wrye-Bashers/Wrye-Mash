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
# Extension for Wrye Mash 0.8.4
#
# (c) D.C.-G. <00:06 14/07/2010>
#
# Published under the exact same terms as the other files of Wrye Mash.
#
# SettingsWindow objects
#
# <13:06 09/08/2010>
#
# Added installers path.
# =============================================================================
from ..localization import _, formatInteger, formatDate

import wx

from ..mosh import GPath, Path
from ..conf import dirs
from .. import conf

dataMap = {
    "Inst"    : "installers",
    "InstData": "installersData",
    "Mw"      : "app",
    "DataDir" : "mods",
}

class SettingsWindow(wx.MiniFrame):
    """Class for the settings_var window."""
    # defining some variables before initialisation
    init = True
    settings_var = None

    def __init__(self, parent=None, id=-1, size=(475, 350),
        pos=wx.DefaultPosition,
        style=wx.DEFAULT_FRAME_STYLE, settings=None):
        """..."""
        wx.MiniFrame.__init__(self, parent=parent, id=id, size=size, pos=pos,
            style=style)
        self.EnableCloseButton(False)
        self.SetTitle(_(u"Wrye Mash Settings"))
        if settings != None:
            self.settings = settings
        else:
            self.settings = {}
        p = self.Panel = wx.Panel(self)
        # components and sizers
        btnOK = wx.Button(p, wx.ID_OK, _(u"Ok"), name=u"btnOK")
        btnCancel = wx.Button(p, wx.ID_CANCEL, _(u"Cancel"), name=u"btnCancel")

        btnBrowseMw = wx.Button(p, wx.ID_OPEN, _(u"..."), size=(-1, -1),
            name=u"btnBrowseMw")
        boxMwDir = wx.StaticBox(p, -1, _(u"Morrowind directory (Morrowind.exe)"))
        self.fldMw = wx.TextCtrl(p, -1, name=u"fldMw")
        sizerBoxMwDir = wx.StaticBoxSizer(boxMwDir, wx.HORIZONTAL)
        sizerBoxMwDir.AddMany(
            [(self.fldMw, 1, wx.EXPAND), ((2, 0)), (btnBrowseMw, 0)])

        btnBrowseInst = wx.Button(p, wx.ID_OPEN, _(u"..."), size=(-1, -1),
            name=u"btnBrowseInst")
        boxInst = wx.StaticBox(p, -1, _(u"Mods installers (*.rar, *.zip, *.7z)"))
        self.fldInst = wx.TextCtrl(p, -1, name=u"fldInst")
        sizerBoxInstallersDir = wx.StaticBoxSizer(boxInst, wx.HORIZONTAL)
        sizerBoxInstallersDir.AddMany(
            [(self.fldInst, 1, wx.EXPAND), ((2, 0)), (btnBrowseInst, 0)])

        btnBrowseDataDir = wx.Button(p, wx.ID_OPEN, _(u"..."), size=(-1, -1),
            name=u"btnBrowseDataDir")
        boxDataDir = wx.StaticBox(p, -1, _(u"Data Files (*.esp, *.esm)"))
        self.fldDataDir = wx.TextCtrl(p, -1, name=u"fldDataDir")
        sizerBoxDataDir = wx.StaticBoxSizer(boxDataDir, wx.HORIZONTAL)
        sizerBoxDataDir.AddMany(
            [(self.fldDataDir, 1, wx.EXPAND), ((2, 0)), (btnBrowseDataDir, 0)])

        btnBrowseInstData = wx.Button(p, wx.ID_OPEN, _(u"..."), size=(-1, -1),
            name=u"btnBrowseInstData")
        boxInstData = wx.StaticBox(p, -1, _(u"Installer Data (installers.dat)"))
        self.fldInstData = wx.TextCtrl(p, -1, name=u"fldInstData")
        sizerBoxInstData = wx.StaticBoxSizer(boxInstData, wx.HORIZONTAL)
        sizerBoxInstData.AddMany(
            [(self.fldInstData, 1, wx.EXPAND), ((2, 0)), (btnBrowseInstData, 0)])

        sizerFields = wx.BoxSizer(wx.VERTICAL)
        sizerFields.AddMany([
            (sizerBoxMwDir,         0, wx.EXPAND), ((0, 2)),
            (sizerBoxInstallersDir, 0, wx.EXPAND), ((0, 2)),
            (sizerBoxInstData, 0, wx.EXPAND), ((0, 2)),
            (sizerBoxDataDir, 0, wx.EXPAND)
        ])
        sizerBtn = wx.BoxSizer(wx.HORIZONTAL)
        sizerBtn.AddMany([(btnOK), ((2, 0), 0, wx.EXPAND), (btnCancel)])
        sizerWin = wx.BoxSizer(wx.VERTICAL)
        sizerWin.AddMany([(sizerFields, 0, wx.EXPAND), ((0, 2)), (sizerBtn)])
        p.SetSizer(sizerWin)
        sizer = wx.BoxSizer()
        sizer.Add(p, 1, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Fit(p)
        self.SetSizeHints(self.GetSize()[0], sizerWin.Size[1])
        self.Fit()
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self.OnCancel)
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOk)
        wx.EVT_BUTTON(self, wx.ID_OPEN, self.OnBrowse)
        wx.EVT_SIZE(self, self.OnSize)

    def OnSize(self, event):
        """..."""
        self.Layout()
        if self.init == True:
            self.SetSizeHints(*self.GetSize())
            self.init = False

    def OnBrowse(self, event):
        """Chosing Morrowind directory."""
        name = event.EventObject.Name[9:]
        dialog = wx.DirDialog(self, _(u"{!s} directory selection".format(dataMap[name]).capitalize()))
        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return
        path = dialog.GetPath()
        dialog.Destroy()
        getattr(self, "fld{!s}".format(name)).SetValue(path)

    def OnCancel(self, event):
        """Cancel button handler."""
        self.Close()

    def OnOk(self, event):
        """Ok button handler."""
        self.settings_var["mwDir"] = self.fldMw.GetValue()
        self.settings_var["installersData"] = self.fldInstData.GetValue()
        for item in self.Panel.GetChildren():
            if item.Name.startswith("fld") == True and item.Name[3:] in dataMap:
                name = dataMap[item.Name[3:]]
                if name in dirs:
                    conf.dirs[name] = GPath(item.GetValue())
        conf.settings['mwDir'] = conf.dirs['app'].s
        conf.settings['installersData'] = conf.dirs['installersData'].s
        conf.settings['sInstallersDir'] = conf.dirs['installers'].s
        self.Close()

    def Close(self):
        """..."""
        self.settings_var["mash.settings.show"] = False
        # self.settings.save()
        wx.MiniFrame.Close(self)

    def SetSettings(self, settings_var, **kwargs):
        """External settings change."""
        self.settings_var = settings_var
        self.fldMw.SetValue(self.settings_var["mwDir"])
        self.fldInstData.SetValue(self.settings_var["installersData"])
        if kwargs != {}:
            for a in kwargs.keys():
                item = getattr(self, "fld{!s}".format(a), None)
                if item:
                    item.SetValue(kwargs[a])
