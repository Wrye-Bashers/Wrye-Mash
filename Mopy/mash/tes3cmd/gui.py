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
import os
from copy import copy

import wx

from .. import tes3cmd
from . import tes3cmdgui


class OutputParserMixin:
    """
    Thi is a mixin to allow unit testing, as we cannot initiate Cleaner
    without a lot of faf with wx
    """

    def ParseOutput(self, output):
        """ Parses the output for a single mod """
        stats = ''
        cleaned = ''
        inStats = False

        for line in output.split('\n'):
            if inStats and line.strip():
                stats += line.strip() + '\n'
            elif line.strip().startswith('Cleaned'):
                cleaned += line.strip() + '\n'
            elif line.strip().startswith('Cleaning Stats for'):
                inStats = True
            elif line.strip().endswith('was not modified'):
                stats += line + '\n'

        return stats, cleaned


class CleanOp(tes3cmdgui.cleanop):
    def __init__(self, parent):
        tes3cmdgui.cleanop.__init__(self, parent)

    def OnCancel(self, event):
        pass

    def OnCleanClick(self, event):
        pass


DONE_HEADER, DONE_CLEAN = range(2)

# the thread that manages the threaded process uses wx events
# to post messsages to the main thread
EVT_DONE_ID = wx.NewId()


def EVT_DONE(win, func):
    win.Connect(-1, -1, EVT_DONE_ID, func)


class DoneEvent(wx.PyEvent):
    def __init__(self, t):
        self.doneType = t
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DONE_ID)


class Cleaner(tes3cmdgui.cleaner, OutputParserMixin):
    """
    GUI interface for the clean function


    It holds a list of files to clean. When Start() is called it works down the
    list of files by calling StartNext which pops a file off the list of files
    and processes it. When the processing of that file is finished OnDone is
    called
    """

    def __init__(self, parent, files, args={}):
        """
        parent - Parent window
        files - list of files to clean
        args - arguemtns to pass to the tes3cmd.threaded class
        """
        tes3cmdgui.cleaner.__init__(self, parent)

        self.args = args

        self.files = files
        self.remainingFiles = copy(files)

        self.output = {}

        EVT_DONE(self, self.OnDone)

    # --------------------------------------------------------------------------
    def Start(self, callback=None):
        """
        Starts running tes3cmd over all the files

        callback - The function that is called when the process is complete
        """
        self.endCallback = callback
        self.StartNext()

    def StartNext(self):
        """
        Starts processing the next file on the list of files. If there are no
        files to process this calls the callback function as defined in the
        call to Start()

        This is called from Start() to start cleaning the list of files
        and from DoneHeadere() to start cleaning the next file when one has been
        cleaned.
        """

        if not self.remainingFiles:
            self.mSkip.Disable()
            self.mStop.Disable()
            if self.endCallback:
                self.endCallback()
            return

        self.currentFile = filename = self.remainingFiles.pop()
        lowerFname = filename.lower()

        # we don't want to clean morrowind.esm
        if lowerFname == 'morrowind.esm':
            self.StartNext()
            return

        # if we copy expansions, don't clean gmsts (I think)
        args = copy(self.args)
        if lowerFname == 'tribunal.esm' or lowerFname == 'bloodmon.esm':
            args['gmsts'] = False
        args['replace'] = True

        self.mCurrentFile.SetLabel(filename)

        # start cleaning the current file
        func = lambda: wx.PostEvent(self, DoneEvent(DONE_CLEAN))
        self.cleaner = tes3cmd.Threaded(callback=func)
        self.cleaner.clean([filename], **args)

    # --------------------------------------------------------------------------
    # GUI clean event and event handlers
    def OnDone(self, event):
        """
        Called when a file has finished processing.
        Dispatches to the correct function depending on event type
        """
        if event.doneType == DONE_HEADER:
            self.DoneHeader()
        elif event.doneType == DONE_CLEAN:
            self.DoneClean()

    def DoneClean(self):
        """
        When the file has done cleaning, we then sync the headers
        """
        out = self.cleaner.out
        err = self.cleaner.err

        stats, cleaned = self.ParseOutput(out)
        self.output[self.currentFile] = {'stats': stats,
            'cleaned'                           : cleaned,
            'output'                            : out,
            'error'                             : err}

        func = lambda: wx.PostEvent(self, DoneEvent(DONE_HEADER))
        self.syncer = tes3cmd.Threaded(callback=func)
        self.syncer.header(self.currentFile)

    def DoneHeader(self):
        """
        When the header has been processed, we can then start the next file
        """
        self.output[self.currentFile]['output'] += self.syncer.out
        self.output[self.currentFile]['error'] += self.syncer.err
        self.mCleanedMods.Append(self.currentFile)

        if not self.mCleanedMods.GetSelections():
            self.mCleanedMods.Select(0)
            self.Select(self.currentFile)

        tfLen = len(self.files)
        ratio = (tfLen - len(self.remainingFiles)) / float(tfLen)
        self.mProgress.SetValue(ratio * 100)

        self.mCurrentFile.SetLabel('')
        self.StartNext()

    # --------------------------------------------------------------------------
    # GUI  skip and stop events
    def OnSkip(self, event):
        """ When the skip button is pressed """
        self.cleaner.stop()
        self.cleaner.join()
        self.StartNext()

    def OnStop(self, event):
        """ When the stop button is pressed """
        self.cleaner.stop()
        self.cleaner.join()

        self.mCurrentFile.SetLabel('')

    # --------------------------------------------------------------------------
    # GUI list selection events to view the logs for a file
    def OnSelect(self, event):
        """ ListBox select, selecting a mod to view the stats of """
        self.Select(event.GetString())

    def Select(self, name):
        """ Sets the details for the given mod name """
        item = self.output[name]
        self.mStats.SetLabel(item['stats'])
        self.mLog.SetValue(item['cleaned'])
        self.mErrors.SetValue(item['error'])

    # --------------------------------------------------------------------------
    # Log functions and save log button event
    def GetLog(self, fileName):
        """ Gets the log text for the given file name """
        log = ''
        o = self.output[fileName]
        if o['error']:
            log += o['error'] + '\n'
        if o['output']:
            log += o['output'] + '\n'
        return log

    def SaveLog(self, fileName):
        """ Saves the log information to the given location """
        f = open(fileName, 'w')
        for fn in self.output.keys():
            f.write('--' + fn + '--\n')
            f.write(self.GetLog(fn))
        f.close()

    def OnSaveLog(self, event):
        dlg = wx.FileDialog(self, 'Save log', os.getcwd(),
            'tes3cmd.log', '*.log',
            wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            fileName = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
            self.SaveLog(fileName)
