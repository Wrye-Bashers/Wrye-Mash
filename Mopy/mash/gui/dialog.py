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
from ..localization import _, formatInteger, formatDate

import wx

from .. import globalvars
from .. import mosh
from .. import exception
from .. import conf


class ProgressDialog(mosh.Progress):
    """Prints progress to file (stdout by default)."""
    # TODO: Look at code to use bolt.class Progress

    def __init__(self, title=_(u'Progress'), message=u'', parent=None,
        style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME, interval=0.1):
        self.dialog = wx.ProgressDialog(title, message, 100, parent, style)
        mosh.Progress.__init__(self, interval)
        self.isDestroyed = False

    def doProgress(self, progress, message):
        if self.dialog:
            self.dialog.Update(int(progress * 100), message)
        else:
            raise exception.InterfaceError, _(u'Dialog already destroyed.')

    def Destroy(self):
        if self.dialog:
            self.dialog.Destroy()
            self.dialog = None


def TextEntry(parent, message, default=u''):
    """Shows a text entry dialog and returns result or None if canceled."""
    dialog = wx.TextEntryDialog(parent, message, default)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        value = dialog.GetValue()
        dialog.Destroy()
        return value


def DirDialog(parent, message=_(u'Choose a directory.'), defaultPath=u''):
    """Shows a modal directory dialog and return the resulting path, or None if canceled."""
    dialog = wx.DirDialog(parent, message, defaultPath,
        style=wx.DD_NEW_DIR_BUTTON)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        path = dialog.GetPath()
        dialog.Destroy()
        return path


def ContinueQuery(parent, message, continueKey, title=_(u'Warning')):
    """Shows a modal continue query if value of continueKey is false. Returns True to continue.
    Also provides checkbox "Don't show this in future." to set continueKey to true."""
    # --ContinueKey set?
    if conf.settings.get(continueKey):
        return wx.ID_OK
    # --Generate/show dialog
    dialog = wx.Dialog(parent, -1, title, size=(350, 200),
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    sizer = wx.BoxSizer(wx.VERTICAL)
    staticText = wx.StaticText(dialog, -1, message, style=wx.ST_NO_AUTORESIZE)
    sizer.Add(staticText, 1, wx.EXPAND | wx.ALL, 6)
    checkBox = wx.CheckBox(dialog, -1, _(u"Don't show this in the future."))
    sizer.Add(checkBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
    # --Save/Cancel
    sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_h1.Add((0, 0), 1)
    sizer_h1.Add(wx.Button(dialog, wx.ID_OK))
    sizer_h1.Add(wx.Button(dialog, wx.ID_CANCEL), 0, wx.LEFT, 4)
    sizer.Add(sizer_h1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
    dialog.SetSizer(sizer)
    # --Get continue key setting and return
    result = dialog.ShowModal()
    if checkBox.GetValue():
        conf.settings[continueKey] = 1
    return result


def LogMessage(parent, message, logText, title=u'', style=0, asDialog=True):
    # --Query Dialog
    pos = conf.settings.get('mash.message.log.pos', wx.DefaultPosition)
    size = conf.settings.get('mash.message.log.size', (400, 400))
    if asDialog:
        window = wx.Dialog(parent, -1, title, pos=pos, size=size,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    else:
        window = wx.Frame(parent, -1, title, pos=pos, size=(200, 300),
            style=(wx.RESIZE_BORDER | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN))
        window.SetIcons(globalvars.images['mash.icons2'].GetIconBundle())
    window.SetSizeHints(200, 200)
    sizer = wx.BoxSizer(wx.VERTICAL)
    if message:
        sizer.Add(wx.StaticText(window, -1, message), 0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)
    textCtrl = wx.TextCtrl(window, -1, logText,
        style=wx.TE_READONLY | wx.TE_MULTILINE)
    sizer.Add(textCtrl, 1, wx.EXPAND)  # |wx.ALL,6)
    window.SetSizer(sizer)
    if asDialog:
        window.ShowModal()
        # --Done
        conf.settings['mash.message.log.pos'] = window.GetPosition()
        conf.settings['mash.message.log.size'] = window.GetSizeTuple()
        window.Destroy()
    else:
        window.Show()


def InfoMessage(parent, message, title=_(u'Information'),
    style=(wx.OK | wx.ICON_INFORMATION)):
    """Shows a modal information message."""
    return Message(parent, message, title, style)


def WarningQuery(parent, message, title=u'',
    style=(wx.YES_NO | wx.ICON_EXCLAMATION)):
    """Shows a modal warning message."""
    return Message(parent, message, title, style)


def WarningMessage(parent, message, title=_(u'Warning'),
    style=(wx.OK | wx.ICON_EXCLAMATION)):
    """Shows a modal warning message."""
    return Message(parent, message, title, style)


def ErrorMessage(parent, message, title=_(u'Error'),
    style=(wx.OK | wx.ICON_HAND)):
    """Shows a modal error message."""
    return Message(parent, message, title, style)


def Message(parent, message, title=u'', style=wx.OK):
    """Shows a modal MessageDialog.
    Use ErrorMessage, WarningMessage or InfoMessage."""
    dialog = wx.MessageDialog(parent, message, title, style)
    result = dialog.ShowModal()
    dialog.Destroy()
    return result
