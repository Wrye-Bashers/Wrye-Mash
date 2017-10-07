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
# Imports ---------------------------------------------------------------------
import sys
import localization
import exception

# File logger-------------------------------------------------------------------
class ErrorLogger:
    """Class can be used for a writer to write to multiple streams. Duplicated
    in both possible startup files so log can be created without external
    dependacies"""

    def __init__(self, outStream):
        self.outStream = outStream

    def write(self, message):
        for s in self.outStream:
            s.write(message)


# Functions used in startup ----------------------------------------------------
def CheckWx():
    """Checks wx is installed, and tries to alert the user"""
    msg = ("You need to install wxPython."
           + "See the Wrye Mash readme for more info!")
    try:
        import wx
    except ImportError:
        try:  # the default win install comes with Tkinter iirc...
            import Tkinter
            import tkMessageBox
            tk = Tkinter.Tk()
            tk.withdraw()  # hide the main window
            tkMessageBox.showwarning("wxPython Not Found!", msg)
            tk.destroy()
            sys.exit(1)
        except ImportError:
            print(msg)
            raise  # dump the info to sdterr


def main(opts):
    CheckWx()

    # Setup log file ---------------------------------------------------------------
    f = file("WryeMash.log", "w+")
    sys.stdout = ErrorLogger([f, sys.__stdout__])
    sys.stderr = ErrorLogger([f, sys.__stderr__])
    f.write("Wrye Mash Log!\n")


    # required to be able to run this with py2exe
    from wx.lib.pubsub import setupv1
    from wx.lib.pubsub import Publisher

    import masher

    # logging and showing of stdout is handled by our code. See errorlog.py
    app = masher.MashApp(redirect=False)
    app.MainLoop()
