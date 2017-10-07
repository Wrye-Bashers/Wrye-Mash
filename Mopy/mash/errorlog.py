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
"""
WxPython contains code for logging output to a file, or logging output to
a window. I really want to do both.

The startup code redirects stdin/stderr to a file, so this class allows
provides a wrapper around stdin/stderr
"""

import sys
import wx


class WxOutputRedirect:
    def __init__(self, std, frame, log):
        self.std = std
        self.frame = frame
        self.log = log

    def write(self, message):
        wx.CallAfter(self.frame.Show)
        wx.CallAfter(self.frame.Raise)
        wx.CallAfter(self.log.WriteText, message)
        wx.CallAfter(self.std.write, message)


class ErrorLog(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, 'Output Log')
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(panel, wx.ID_ANY,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL | wx.EXPAND)
        panel.SetSizer(sizer)

        sys.stdout = WxOutputRedirect(sys.stdout, self, log)
        sys.stderr = WxOutputRedirect(sys.stderr, self, log)

    def OnClose(self, evt):
        self.Hide()
