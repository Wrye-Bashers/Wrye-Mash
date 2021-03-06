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
import cStringIO
import string
import struct
import sys
import textwrap
import time
import exception

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from localization import _, formatInteger, formatDate

import bolt
from bolt import GPath, deprint, delist
import conf


# Basics ---------------------------------------------------------------------
class IdList:
    """Provides sequences of semi-unique ids. Useful for choice menus.

    Sequence ids come in range from baseId up through (baseId + size - 1).
    Named ids will be assigned ids starting at baseId + size.

    Example:
      loadIds = IdList(10000, 90,'SAVE','EDIT','NONE')
    sequence ids are accessed by an iterator: i.e. iter(loadIds), and
    named ids accessed by name. e.g. loadIds.SAVE, loadIds.EDIT, loadIds.NONE
    """

    def __init__(self, baseId, size, *names):
        self.BASE = baseId
        self.MAX = baseId + size - 1
        # --Extra
        nextNameId = baseId + size
        for name in names:
            setattr(self, name, nextNameId)
            nextNameId += 1

    def __iter__(self):
        """Return iterator."""
        for id in range(self.BASE, self.MAX + 1):
            yield id


# Constants -------------------------------------------------------------------
defId = wx.ID_ANY
defVal = wx.DefaultValidator
defPos = wx.DefaultPosition
defSize = wx.DefaultSize
defBitmap =  wx.NullBitmap

wxListAligns = {
    'LEFT'  : wx.LIST_FORMAT_LEFT,
    'RIGHT' : wx.LIST_FORMAT_RIGHT,
    'CENTER': wx.LIST_FORMAT_CENTRE,
}

# Settings --------------------------------------------------------------------
_settings = {}  # --Using applications should override this.
sizes = {}  # --Using applications should override this.


# Colors ----------------------------------------------------------------------
class Colors:
    """Colour collection and wrapper for wx.ColourDatabase.
    Provides dictionary syntax access (colors[key]) and predefined colours."""

    def __init__(self):
        self._colors = {}

    def __setitem__(self, key, value):
        """Add a color to the database."""
        if not isinstance(value, str):
            self._colors[key] = wx.Colour(*value)
        else:
            self._colors[key] = value

    def __getitem__(self, key):
        """Dictionary syntax: color = colours[key]."""
        if key in self._colors:
            key = self._colors[key]
            if not isinstance(key, str):
                return key
        return wx.TheColourDatabase.Find(key)

    def __iter__(self):
        for key in self._colors:
            yield key


# --Singleton
colors = Colors()

# Images ----------------------------------------------------------------------
images = {}  # --Singleton for collection of images.


# ------------------------------------------------------------------------------
class Image:
    """Wrapper for images, allowing access in various formats/classes.

    Allows image to be specified before wx.App is initialized."""

    typesDict = {
        'png' : wx.BITMAP_TYPE_PNG,
        'jpg' : wx.BITMAP_TYPE_JPEG,
        'jpeg': wx.BITMAP_TYPE_JPEG,
        'ico' : wx.BITMAP_TYPE_ICO,
        'bmp' : wx.BITMAP_TYPE_BMP,
        'tif' : wx.BITMAP_TYPE_TIF,
    }

    def __init__(self, filename, imageType=None, iconSize=16):
        self.file = GPath(filename)
        try:
            self._img_type = imageType or self.typesDict[self.file.cext[1:]]
        except KeyError:
            deprint(u'Unknown image extension {!s}'.format(self.file.cext))
            self._img_type = wx.BITMAP_TYPE_ANY
        self.bitmap = None
        self.icon = None
        self.iconSize = iconSize
        # if not GPath(self.file).exists():
        if not GPath(self.file.s.split(u';')[0]).exists():
            raise exception.ArgumentError(
                _(u'Missing resource file: {!s}.'.format(self.file)))

    def GetBitmap(self):
        if not self.bitmap:
            if self._img_type == wx.BITMAP_TYPE_ICO:
                self.GetIcon()
                w, h = self.icon.GetWidth(), self.icon.GetHeight()
                self.bitmap = wx.EmptyBitmap(w, h)
                self.bitmap.CopyFromIcon(self.icon)
                # Hack - when user scales windows display icon may need scaling
                if w != self.iconSize or h != self.iconSize:  # rescale !
                    self.bitmap = wx.BitmapFromImage(
                        wx.ImageFromBitmap(self.bitmap).Scale(
                            self.iconSize, self.iconSize,
                            wx.IMAGE_QUALITY_HIGH))
            else:
                self.bitmap = wx.Bitmap(self.file.s, self._img_type)
        return self.bitmap

    def GetIcon(self):
        if not self.icon:
            if self._img_type == wx.BITMAP_TYPE_ICO:
                self.icon = wx.Icon(self.file.s, wx.BITMAP_TYPE_ICO,
                    self.iconSize, self.iconSize)
                # we failed to get the icon? (when display resolution changes)
                if not self.icon.GetWidth() or not self.icon.GetHeight():
                    self.icon = wx.Icon(self.file.s, wx.BITMAP_TYPE_ICO)
            else:
                self.icon = wx.EmptyIcon()
                self.icon.CopyFromBitmap(self.GetBitmap())
        return self.icon

    @staticmethod
    def GetImage(image_data, height, width):
        """Hasty wrapper around wx.EmptyImage - absorb to GetBitmap."""
        image = wx.EmptyImage(width, height)
        image.SetData(image_data)
        return image

    @staticmethod
    def Load(srcPath, quality):
        """Hasty wrapper around wx.Image - loads srcPath with specified
        quality if a jpeg."""
        bitmap = wx.Image(srcPath.s)
        # This only has an effect on jpegs, so it's ok to do it on every kind
        bitmap.SetOptionInt(wx.IMAGE_OPTION_QUALITY, quality)
        return bitmap


#------------------------------------------------------------------------------
class ImageBundle:
    """Wrapper for bundle of images.

    Allows image bundle to be specified before wx.App is initialized."""

    def __init__(self):
        self._image_paths = []
        self.iconBundle = None

    def Add(self, img_path):
        self._image_paths.append(img_path)

    def GetIconBundle(self):
        if not self.iconBundle:
            self.iconBundle = wx.IconBundle()
            for img_path in self._image_paths:
                self.iconBundle.AddIcon(img_path.GetIcon())
        return self.iconBundle


# ------------------------------------------------------------------------------
class ImageList:
    """Wrapper for wx.ImageList.

    Allows ImageList to be specified before wx.App is initialized.
    Provides access to ImageList integers through imageList[key]."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = []
        self.indices = {}
        self.imageList = None

    def Add(self, image, key):
        self.data.append((key, image))

    def GetImageList(self):
        if not self.imageList:
            indices = self.indices
            imageList = self.imageList = wx.ImageList(self.width, self.height)
            for key, image in self.data:
                indices[key] = imageList.Add(image.GetBitmap())
        return self.imageList

    def __getitem__(self, key):
        self.GetImageList()
        return self.indices[key]


# Functions -------------------------------------------------------------------
def fill(text, width=60):
    """Wraps paragraph to width characters."""
    pars = [textwrap.fill(text, width) for text in text.split(u'\n')]
    return u'\n'.join(pars)


def ensureDisplayed(frame, x=100, y=100):
    """Ensure that frame is displayed."""
    if wx.Display.GetFromWindow(frame) == -1:
        topLeft = wx.Display(0).GetGeometry().GetTopLeft()
        frame.MoveXY(topLeft.x + x, topLeft.y + y)


def setCheckListItems(checkListBox, names, values):
    """Convenience method for setting a bunch of wxCheckListBox items. The
    main advantage of this is that it doesn't clear the list unless it needs
    to. Which is good if you want to preserve the scroll position of the list.
    """
    if not names:
        checkListBox.Clear()
    else:
        for index, (name, value) in enumerate(zip(names, values)):
            if index >= checkListBox.GetCount():
                checkListBox.Append(name)
            else:
                if index == -1:
                    deprint(u'index = -1, name = {!s}, value = {!s}'.format(name, value))
                    continue
                checkListBox.SetString(index, name)
            checkListBox.Check(index, value)
        for index in range(checkListBox.GetCount(), len(names), -1):
            checkListBox.Delete(index - 1)


# Elements --------------------------------------------------------------------
def bell(arg=None):
    """Rings the system bell and returns the input argument (useful for return bell(value))."""
    wx.Bell()
    return arg


def tooltip(text, wrap=50):
    """Returns tolltip with wrapped copy of text."""
    text = textwrap.fill(text, wrap)
    return wx.ToolTip(text)


# Wxpython Check for 4.0
# validator=DefaultValidator: was val
def bitmapButton(parent, id=defId, bitmap=defBitmap, pos=defPos, size=defSize,
    style=wx.BU_AUTODRAW, val=defVal, name=u'button', onClick=None, tip=None):
    """Creates a button, binds click function, then returns bound button."""
    gButton = wx.BitmapButton(parent, id, bitmap, pos, size, style, val, name)
    if onClick:
        gButton.Bind(wx.EVT_BUTTON, onClick)
    if tip:
        gButton.SetToolTip(tooltip(tip))
    return gButton


def button(parent, label=u'', pos=defPos, size=defSize, style=0, val=defVal,
    name=u'button', id=defId, onClick=None, tip=None):
    """Creates a button, binds click function, then returns bound button."""
    gButton = wx.Button(parent, id, label, pos, size, style, val, name)
    if onClick:
        gButton.Bind(wx.EVT_BUTTON, onClick)
    if tip:
        gButton.SetToolTip(tooltip(tip))
    return gButton


def toggleButton(parent, label=u'', pos=defPos, size=defSize, style=0,
    val=defVal, name=u'button', id=defId, onClick=None, tip=None):
    """Creates a toggle button, binds toggle function, then returns bound button."""
    gButton = wx.ToggleButton(parent, id, label, pos, size, style, val, name)
    if onClick:
        gButton.Bind(wx.EVT_TOGGLEBUTTON, onClick)
    if tip:
        gButton.SetToolTip(tooltip(tip))
    return gButton


def checkBox(parent, label=u'', pos=defPos, size=defSize, style=0, val=defVal,
    name=u'checkBox', id=defId, onCheck=None, tip=None):
    """Creates a checkBox, binds check function, then returns bound button."""
    gCheckBox = wx.CheckBox(parent, id, label, pos, size, style, val, name)
    if onCheck:
        gCheckBox.Bind(wx.EVT_CHECKBOX, onCheck)
    if tip:
        gCheckBox.SetToolTip(tooltip(tip))
    return gCheckBox


def staticText(parent, label=u'', pos=defPos, size=defSize, style=0,
    name=u"staticText", id=defId, ):
    """Static text element."""
    return wx.StaticText(parent, id, label, pos, size, style, name)


def spinCtrl(parent, value=u'', pos=defPos, size=defSize,
    style=wx.SP_ARROW_KEYS, min=0, max=100, initial=0, name=u'wxSpinctrl',
    id=defId, onSpin=None, tip=None):
    """Spin control with event and tip setting."""
    gSpinCtrl = wx.SpinCtrl(parent, id, value, pos, size, style, min, max,
        initial, name)
    if onSpin:
        gSpinCtrl.Bind(wx.EVT_SPINCTRL, onSpin)
    if tip:
        gSpinCtrl.SetToolTip(tooltip(tip))
    return gSpinCtrl


# Sub-Windows -----------------------------------------------------------------
def leftSash(parent, defaultSize=(100, 100), onSashDrag=None):
    """Creates a left sash window."""
    sash = wx.SashLayoutWindow(parent, style=wx.SW_3D)
    sash.SetDefaultSize(defaultSize)
    sash.SetOrientation(wx.LAYOUT_VERTICAL)
    sash.SetAlignment(wx.LAYOUT_LEFT)
    sash.SetSashVisible(wx.SASH_RIGHT, True)
    if onSashDrag:
        id = sash.GetId()
        sash.Bind(wx.EVT_SASH_DRAGGED_RANGE, onSashDrag, id=id, id2=id)
    return sash


def topSash(parent, defaultSize=(100, 100), onSashDrag=None):
    """Creates a top sash window."""
    sash = wx.SashLayoutWindow(parent, style=wx.SW_3D)
    sash.SetDefaultSize(defaultSize)
    sash.SetOrientation(wx.LAYOUT_HORIZONTAL)
    sash.SetAlignment(wx.LAYOUT_TOP)
    sash.SetSashVisible(wx.SASH_BOTTOM, True)
    if onSashDrag:
        id = sash.GetId()
        sash.Bind(wx.EVT_SASH_DRAGGED_RANGE, onSashDrag, id=id, id2=id)
    return sash


# Sizers ----------------------------------------------------------------------
spacer = ((0, 0), 1)  # --Used to space elements apart.


def aSizer(sizer, *elements):
    """Adds elements to a sizer."""
    for element in elements:
        if isinstance(element, tuple):
            if element[0] != None:
                sizer.Add(*element)
        elif element != None:
            sizer.Add(element)
    return sizer


def hSizer(*elements):
    """Horizontal sizer."""
    return aSizer(wx.BoxSizer(wx.HORIZONTAL), *elements)


def vSizer(*elements):
    """Vertical sizer and elements."""
    return aSizer(wx.BoxSizer(wx.VERTICAL), *elements)


def hsbSizer(boxArgs, *elements):
    """Horizontal static box sizer and elements."""
    return aSizer(wx.StaticBoxSizer(wx.StaticBox(*boxArgs), wx.HORIZONTAL),
        *elements)


def vsbSizer(boxArgs, *elements):
    """Vertical static box sizer and elements."""
    return aSizer(wx.StaticBoxSizer(wx.StaticBox(*boxArgs), wx.VERTICAL),
        *elements)


# Modal Dialogs ---------------------------------------------------------------
# ------------------------------------------------------------------------------
def askDirectory(parent, message=_('Choose a directory.'), defaultPath=''):
    """Shows a modal directory dialog and return the resulting path, or None if canceled."""
    dialog = wx.DirDialog(parent, message, GPath(defaultPath).s,
        style=wx.DD_NEW_DIR_BUTTON)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        path = dialog.GetPath()
        dialog.Destroy()
        return path


# ------------------------------------------------------------------------------
def askContinue(parent, message, continueKey, title=_(u'Warning')):
    """Shows a modal continue query if value of continueKey is false. Returns True to continue.
    Also provides checkbox "Don't show this in future." to set continueKey to true."""
    # --ContinueKey set?
    if _settings.get(continueKey):
        return wx.ID_OK
    # --Generate/show dialog
    dialog = wx.Dialog(parent, defId, title, size=(350, 200),
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    icon = wx.StaticBitmap(dialog, defId,
        wx.ArtProvider_GetBitmap(wx.ART_WARNING, wx.ART_MESSAGE_BOX, (32, 32)))
    gCheckBox = checkBox(dialog, _(u"Don't show this in the future."))
    # --Layout
    sizer = vSizer(
        (hSizer(
            (icon, 0, wx.ALL, 6),
            (staticText(dialog, message, style=wx.ST_NO_AUTORESIZE), 1,
            wx.EXPAND | wx.LEFT, 6),
        ), 1, wx.EXPAND | wx.ALL, 6),
        (gCheckBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6),
        (hSizer(  # --Save/Cancel
            spacer,
            button(dialog, id=wx.ID_OK),
            (button(dialog, id=wx.ID_CANCEL), 0, wx.LEFT, 4),
        ), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6),
    )
    dialog.SetSizer(sizer)
    # --Get continue key setting and return
    result = dialog.ShowModal()
    if gCheckBox.GetValue():
        _settings[continueKey] = 1
    return result in (wx.ID_OK, wx.ID_YES)


# ------------------------------------------------------------------------------
def askOpen(parent, title=u'', defaultDir=u'', defaultFile=u'', wildcard=u'',
    style=wx.OPEN):
    """Show as file dialog and return selected path(s)."""
    defaultDir, defaultFile = [GPath(x).s for x in (defaultDir, defaultFile)]
    dialog = wx.FileDialog(parent, title, defaultDir, defaultFile, wildcard,
        style)
    if dialog.ShowModal() != wx.ID_OK:
        result = False
    elif style & wx.MULTIPLE:
        result = map(GPath, dialog.GetPaths())
    else:
        result = GPath(dialog.GetPath())
    dialog.Destroy()
    return result


def askOpenMulti(parent, title=u'', defaultDir=u'', defaultFile=u'',
    wildcard=u'', style=wx.OPEN | wx.MULTIPLE):
    """Show as save dialog and return selected path(s)."""
    return askOpen(parent, title, defaultDir, defaultFile, wildcard, style)


def askSave(parent, title=u'', defaultDir=u'', defaultFile=u'', wildcard=u'',
    style=wx.OVERWRITE_PROMPT):
    """Show as save dialog and return selected path(s)."""
    return askOpen(parent, title, defaultDir, defaultFile, wildcard,
        wx.SAVE | style)


# ------------------------------------------------------------------------------
def askText(parent, message, title=u'', default=u''):
    """Shows a text entry dialog and returns result or None if canceled."""
    dialog = wx.TextEntryDialog(parent, message, title, default)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        value = dialog.GetValue()
        dialog.Destroy()
        return value


# Message Dialogs -------------------------------------------------------------
def askStyled(parent, message, title, style):
    """Shows a modal MessageDialog.
    Use ErrorMessage, WarningMessage or InfoMessage."""
    dialog = wx.MessageDialog(parent, message, title, style)
    result = dialog.ShowModal()
    dialog.Destroy()
    return result in (wx.ID_OK, wx.ID_YES)


def askOk(parent, message, title=u''):
    """Shows a modal error message."""
    return askStyled(parent, message, title, wx.OK | wx.CANCEL)


def askYes(parent, message, title=u'', default=True):
    """Shows a modal warning message."""
    style = wx.YES_NO | wx.ICON_EXCLAMATION | ((wx.NO_DEFAULT, wx.YES_DEFAULT)[default])
    return askStyled(parent, message, title, style)


def askWarning(parent, message, title=_(u'Warning')):
    """Shows a modal warning message."""
    return askStyled(parent, message, title,
        wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)


def showOk(parent, message, title=u''):
    """Shows a modal error message."""
    return askStyled(parent, message, title, wx.OK)


def showError(parent, message, title=_(u'Error')):
    """Shows a modal error message."""
    return askStyled(parent, message, title, wx.OK | wx.ICON_HAND)


def showWarning(parent, message, title=_(u'Warning')):
    """Shows a modal warning message."""
    return askStyled(parent, message, title, wx.OK | wx.ICON_EXCLAMATION)


def showInfo(parent, message, title=_(u'Information')):
    """Shows a modal information message."""
    return askStyled(parent, message, title, wx.OK | wx.ICON_INFORMATION)


def showList(parent, header, items, maxItems=0, title=u''):
    """Formats a list of items into a message for use in a Message."""
    numItems = len(items)
    if maxItems <= 0:
        maxItems = numItems
    message = string.Template(header).substitute(count=numItems)
    message += u'\n* ' + u'\n* '.join(items[:min(numItems, maxItems)])
    if numItems > maxItems:
        message += _(u'\n(And {:d} others.)'.format(numItems - maxItems))
    return askStyled(parent, message, title, wx.OK)


# ------------------------------------------------------------------------------
def showLogClose(evt=None):
    """Handle log message closing."""
    window = evt.GetEventObject()
    if not window.IsIconized() and not window.IsMaximized():
        conf.settings['balt.LogMessage.pos'] = window.GetPositionTuple()
        conf.settings['balt.LogMessage.size'] = window.GetSizeTuple()
    window.Destroy()


def showLog(parent, logText, title=u'', style=0, asDialog=True, fixedFont=False,
    icons=None):
    """Display text in a log window"""
    # --Sizing
    pos = conf.settings.get('balt.LogMessage.pos', defPos)
    size = conf.settings.get('balt.LogMessage.size', (400, 400))
    # --Dialog or Frame
    if asDialog:
        window = wx.Dialog(parent, defId, title, pos=pos, size=size,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    else:
        window = wx.Frame(parent, defId, title, pos=pos, size=size,
            style=(wx.RESIZE_BORDER | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN))
        if icons:
            window.SetIcons(icons)
    window.SetSizeHints(200, 200)
    window.Bind(wx.EVT_CLOSE, showLogClose)
    window.SetBackgroundColour(
        wx.NullColour)  # --Bug workaround to ensure that default colour is being used.
    # --Text
    textCtrl = wx.TextCtrl(window, defId, logText,
        style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2 | wx.SUNKEN_BORDER)
    if fixedFont:
        fixedFont = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT)
        fixedFont.SetPointSize(8)
        fixedStyle = wx.TextAttr()
        # fixedStyle.SetFlags(0x4|0x80)
        fixedStyle.SetFont(fixedFont)
        textCtrl.SetStyle(0, textCtrl.GetLastPosition(), fixedStyle)
    # --Buttons
    gOkButton = button(window, id=wx.ID_OK,
        onClick=lambda event: window.Close())
    gOkButton.SetDefault()
    # --Layout
    window.SetSizer(
        vSizer(
            (textCtrl, 1, wx.EXPAND | wx.ALL ^ wx.BOTTOM, 2),
            (gOkButton, 0, wx.ALIGN_RIGHT | wx.ALL, 4),
        )
    )
    # --Show
    if asDialog:
        window.ShowModal()
        window.Destroy()
    else:
        window.Show()


# ------------------------------------------------------------------------------
def showWryeLog(parent, logText, title=u'', style=0, asDialog=True, icons=None):
    """Convert logText from wtxt to html and display. Optionally, logText can be path to an html file."""
    import wx.lib.iewin
    # --Sizing
    pos = conf.settings.get('balt.WryeLog.pos', defPos)
    size = conf.settings.get('balt.WryeLog.size', (400, 400))
    # --Dialog or Frame
    if asDialog:
        window = wx.Dialog(parent, defId, title, pos=pos, size=size,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    else:
        window = wx.Frame(parent, defId, title, pos=pos, size=size,
            style=(wx.RESIZE_BORDER | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN))
        if icons:
            window.SetIcons(icons)
    window.SetSizeHints(200, 200)
    window.Bind(wx.EVT_CLOSE, showLogClose)
    # --Text
    textCtrl = wx.lib.iewin.IEHtmlWindow(window, defId,
        style=wx.NO_FULL_REPAINT_ON_RESIZE)
    if not isinstance(logText, bolt.Path):
        logPath = conf.settings.get('balt.WryeLog.temp',
            bolt.Path.getcwd().join('WryeLogTemp.html'))
        cssDir = conf.settings.get('balt.WryeLog.cssDir', GPath(''))
        ins = cStringIO.StringIO(logText + u'\n{{CSS:wtxt_sand_small.css}}')
        out = logPath.open('w')
        bolt.WryeText.genHtml(ins, out, cssDir)
        out.close()
        logText = logPath
    textCtrl.Navigate(logText.s, 0x2)  # --0x2: Clear History
    # --Buttons
    bitmap = wx.ArtProvider_GetBitmap(wx.ART_GO_BACK, wx.ART_HELP_BROWSER,
        (16, 16))
    gBackButton = bitmapButton(window, bitmap,
        onClick=lambda evt: textCtrl.GoBack())
    bitmap = wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD, wx.ART_HELP_BROWSER,
        (16, 16))
    gForwardButton = bitmapButton(window, bitmap,
        onClick=lambda evt: textCtrl.GoForward())
    gOkButton = button(window, id=wx.ID_OK,
        onClick=lambda event: window.Close())
    gOkButton.SetDefault()
    # --Layout
    window.SetSizer(
        vSizer(
            (textCtrl, 1, wx.EXPAND | wx.ALL ^ wx.BOTTOM, 2),
            (hSizer(
                gBackButton,
                gForwardButton,
                spacer,
                gOkButton,
            ), 0, wx.ALL | wx.EXPAND, 4),
        )
    )
    # --Show
    if asDialog:
        window.ShowModal()
        conf.settings['balt.WryeLog.pos'] = window.GetPositionTuple()
        conf.settings['balt.WryeLog.size'] = window.GetSizeTuple()
        window.Destroy()
    else:
        window.Show()


# Other Windows ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class ListEditorData:
    """Data capsule for ListEditor. [Abstract]"""

    def __init__(self, parent):
        """Initialize."""
        self.parent = parent  # --Parent window.
        self.showAction = False
        self.showAdd = False
        self.showEdit = False
        self.showRename = False
        self.showRemove = False
        self.showSave = False
        self.showCancel = False
        self.caption = None
        # --Editable?
        self.showInfo = False
        self.infoWeight = 1  # --Controls width of info pane
        self.infoReadOnly = True  # --Controls whether info pane is editable

    # --List
    def action(self, item):
        """Called when action button is used.."""
        pass

    def select(self, item):
        """Called when an item is selected."""
        pass

    def getItemList(self):
        """Returns item list in correct order."""
        raise exception.AbstractError
        return []

    def add(self):
        """Peforms add operation. Return new item on success."""
        raise exception.AbstractError
        return None

    def edit(self, item=None):
        """Edits specified item. Return true on success."""
        raise exception.AbstractError
        return False

    def rename(self, oldItem, newItem):
        """Renames oldItem to newItem. Return true on success."""
        raise exception.AbstractError
        return False

    def remove(self, item):
        """Removes item. Return true on success."""
        raise exception.AbstractError
        return False

    def close(self):
        """Called when dialog window closes."""
        pass

    # --Info box
    def getInfo(self, item):
        """Returns string info on specified item."""
        return u''

    def setInfo(self, item, text):
        """Sets string info on specified item."""
        raise exception.AbstractError

    # --Checklist
    def getChecks(self):
        """Returns checked state of items as array of True/False values matching Item list."""
        raise exception.AbstractError
        return []

    def check(self, item):
        """Checks items. Return true on success."""
        raise exception.AbstractError
        return False

    def uncheck(self, item):
        """Unchecks item. Return true on success."""
        raise exception.AbstractError
        return False

    # --Save/Cancel
    def save(self):
        """Handles save button."""
        pass

    def cancel(self):
        """Handles cancel button."""
        pass


# ------------------------------------------------------------------------------
class ListEditor(wx.Dialog):
    """Dialog for editing lists."""

    def __init__(self, parent, id, title, data, type='list'):
        # --Data
        self.data = data  # --Should be subclass of ListEditorData
        self.items = data.getItemList()
        # --GUI
        wx.Dialog.__init__(self, parent, id, title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        # --Caption
        if data.caption:
            captionText = staticText(self, data.caption)
        else:
            captionText = None
        # --List Box
        if type == 'checklist':
            self.list = wx.CheckListBox(self, wx.ID_ANY, choices=self.items,
                style=wx.LB_SINGLE)
            for index, checked in enumerate(self.data.getChecks()):
                self.list.Check(index, checked)
            self.Bind(wx.EVT_CHECKLISTBOX, self.DoCheck, self.list)
        else:
            self.list = wx.ListBox(self, wx.ID_ANY, choices=self.items,
                style=wx.LB_SINGLE)
        self.list.SetSizeHints(125, 150)
        self.list.Bind(wx.EVT_LISTBOX, self.OnSelect)
        # --Infobox
        if data.showInfo:
            self.gInfoBox = wx.TextCtrl(self, wx.ID_ANY, u" ", size=(130, -1),
                style=(
                      self.data.infoReadOnly * wx.TE_READONLY) | wx.TE_MULTILINE | wx.SUNKEN_BORDER)
            if not self.data.infoReadOnly:
                self.gInfoBox.Bind(wx.EVT_TEXT, self.OnInfoEdit)
        else:
            self.gInfoBox = None
        # --Buttons
        buttonSet = (
            (data.showAction, _(u'Action'), self.DoAction),
            (data.showAdd, _(u'Add'), self.DoAdd),
            (data.showEdit, _(u'Edit'), self.DoEdit),
            (data.showRename, _(u'Rename'), self.DoRename),
            (data.showRemove, _(u'Remove'), self.DoRemove),
            (data.showSave, _(u'Save'), self.DoSave),
            (data.showCancel, _(u'Cancel'), self.DoCancel),
        )
        if sum(bool(x[0]) for x in buttonSet):
            buttons = vSizer()
            for (flag, defLabel, func) in buttonSet:
                if not flag:
                    continue
                label = (flag == True and defLabel) or flag
                buttons.Add(button(self, label, onClick=func), 0,
                    wx.LEFT | wx.TOP, 4)
        else:
            buttons = None
        # --Layout
        sizer = vSizer(
            (captionText, 0, wx.LEFT | wx.TOP, 4),
            (hSizer(
                (self.list, 1, wx.EXPAND | wx.TOP, 4),
                (self.gInfoBox, self.data.infoWeight, wx.EXPAND | wx.TOP, 4),
                (buttons, 0, wx.EXPAND),
            ), 1, wx.EXPAND)
        )
        # --Done
        className = data.__class__.__name__
        if className in sizes:
            self.SetSizer(sizer)
            self.SetSize(sizes[className])
        else:
            self.SetSizerAndFit(sizer)

    def GetSelected(self):
        return self.list.GetNextItem(-1, wx.LIST_NEXT_ALL,
            wx.LIST_STATE_SELECTED)

    # --Checklist commands
    def DoCheck(self, event):
        """Handles check/uncheck of listbox item."""
        index = event.GetSelection()
        item = self.items[index]
        if self.list.IsChecked(index):
            self.data.check(item)
        else:
            self.data.uncheck(item)
            # self.list.SetSelection(index)

    # --List Commands
    def DoAction(self, event):
        """Acts on the selected item."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        itemDex = selections[0]
        item = self.items[itemDex]
        self.data.action(item)

    def DoAdd(self, event):
        """Adds a new item."""
        newItem = self.data.add()
        if newItem and newItem not in self.items:
            self.items = self.data.getItemList()
            index = self.items.index(newItem)
            self.list.InsertItems([newItem], index)

    def DoEdit(self, event):
        """Edits the selected item."""
        raise exception.UncodedError

    def DoRename(self, event):
        """Renames selected item."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        # --Rename it
        itemDex = selections[0]
        curName = self.list.GetString(itemDex)
        # --Dialog
        newName = askText(self, _(u'Rename to:'), _(u'Rename'), curName)
        if not newName or newName == curName:
            return
        elif newName in self.items:
            showError(self, _(u'Name must be unique.'))
        elif self.data.rename(curName, newName):
            self.items[itemDex] = newName
            self.list.SetString(itemDex, newName)

    def DoRemove(self, event):
        """Removes selected item."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        # --Data
        itemDex = selections[0]
        item = self.items[itemDex]
        if not self.data.remove(item):
            return
        # --GUI
        del self.items[itemDex]
        self.list.Delete(itemDex)
        if self.gInfoBox:
            self.gInfoBox.DiscardEdits()
            self.gInfoBox.SetValue(u'')

    # --Show Info
    def OnSelect(self, event):
        """Handle show info (item select) event."""
        index = event.GetSelection()
        item = self.items[index]
        self.data.select(item)
        if self.gInfoBox:
            self.gInfoBox.DiscardEdits()
            self.gInfoBox.SetValue(self.data.getInfo(item))

    def OnInfoEdit(self, event):
        """Info box text has been edited."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        item = self.items[selections[0]]
        if self.gInfoBox.IsModified():
            self.data.setInfo(item, self.gInfoBox.GetValue())

    # --Save/Cancel
    def DoSave(self, event):
        """Handle save button."""
        self.data.save()
        sizes[self.data.__class__.__name__] = self.GetSizeTuple()
        self.EndModal(wx.ID_OK)

    def DoCancel(self, event):
        """Handle save button."""
        self.data.cancel()
        sizes[self.data.__class__.__name__] = self.GetSizeTuple()
        self.EndModal(wx.ID_CANCEL)

    # --Window Closing
    def OnCloseWindow(self, event):
        """Handle window close event.
        Remember window size, position, etc."""
        self.data.close()
        sizes[self.data.__class__.__name__] = self.GetSizeTuple()
        self.Destroy()


# ------------------------------------------------------------------------------
class Picture(wx.Window):
    """Picture panel."""

    def __init__(self, parent, width, height, scaling=1, style=0):
        """Initialize."""
        wx.Window.__init__(self, parent, defId, size=(width, height),
            style=style)
        self.scaling = scaling
        self.bitmap = None
        self.scaled = None
        self.oldSize = (0, 0)
        self.SetSizeHints(width, height, width, height)
        # --Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def SetBitmap(self, bitmap):
        """Set bitmap."""
        self.bitmap = bitmap
        self.Rescale()
        self.Refresh()

    def Rescale(self):
        """Updates scaled version of bitmap."""
        picWidth, picHeight = self.oldSize = self.GetSizeTuple()
        bitmap = self.scaled = self.bitmap
        if not bitmap:
            return
        imgWidth, imgHeight = bitmap.GetWidth(), bitmap.GetHeight()
        if self.scaling == 2 or (self.scaling == 1 and (imgWidth > picWidth or imgHeight > picHeight)):
            image = bitmap.ConvertToImage()
            factor = min(1.0 * picWidth / imgWidth, 1.0 * picHeight / imgHeight)
            newWidth, newHeight = int(factor * imgWidth), int(
                factor * imgHeight)
            self.scaled = image.Scale(newWidth, newHeight).ConvertToBitmap()
            # self.scaled = image.Scale(newWidth,newHeight,wx.IMAGE_QUALITY_HIGH ).ConvertToBitmap()

    def OnPaint(self, event=None):
        """Draw bitmap or clear drawing area."""
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.MEDIUM_GREY_BRUSH)
        if self.scaled:
            if self.GetSizeTuple() != self.oldSize:
                self.Rescale()
            panelWidth, panelHeight = self.GetSizeTuple()
            xPos = max(0, (panelWidth - self.scaled.GetWidth()) / 2)
            yPos = max(0, (panelHeight - self.scaled.GetHeight()) / 2)
            dc.Clear()
            dc.DrawBitmap(self.scaled, xPos, yPos, False)
        else:
            dc.Clear()
            # dc.SetPen(wx.Pen("BLACK", 1))
            # dc.SetBrush(wx.TRANSPARENT_BRUSH)
            # (width,height) = self.GetSize()
            # dc.DrawRectangle(0,0,width,height)

    def OnSize(self, event):
        self.Refresh()


# ------------------------------------------------------------------------------
class Progress(bolt.Progress):
    """Progress as progress dialog."""
    _style = wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_SMOOTH

    def __init__(self, title=_(u'Progress'), message=u' ' * 60, parent=None,
        abort=False, elapsed=True, __style=_style):
        if abort:
            __style |= wx.PD_CAN_ABORT
        if elapsed:
            __style |= wx.PD_ELAPSED_TIME
        self.dialog = wx.ProgressDialog(title, message, 100, parent, __style)
        bolt.Progress.__init__(self)
        self.message = message
        self.isDestroyed = False
        self.prevMessage = u''
        self.prevState = -1
        self.prevTime = 0

    # __enter__ and __exit__ for use with the 'with' statement
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.Destroy()

    def getParent(self):
        return self.dialog.GetParent()

    def setCancel(self, enabled=True):
        cancel = self.dialog.FindWindowById(wx.ID_CANCEL)
        cancel.Enable(enabled)

    def _do_progress(self, state, message):
        if not self.dialog:
            raise exception.StateError(u'Dialog already destroyed.')
        elif (state == 0 or state == 1 or (message != self.prevMessage) or
                (state - self.prevState) > 0.05 or (
            time.time() - self.prevTime) > 0.5):
            if message != self.prevMessage:
                ret = self.dialog.Update(int(state * 100), message)
            else:
                ret = self.dialog.Update(int(state * 100))
            if not ret[0]:
                raise exception.CancelError
            self.prevMessage = message
            self.prevState = state
            self.prevTime = time.time()

    def Destroy(self):
        if self.dialog:
            self.dialog.Destroy()
            self.dialog = None


# ------------------------------------------------------------------------------
class Tank(wx.Panel):
    """'Tank' format table. Takes the form of a wxListCtrl in Report mode, with
    multiple columns and (optionally) column an item menus."""

    class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
        """List control extended with the wxPython auto-width mixin class."""

        def __init__(self, parent, id, pos=defPos, size=defSize, style=0):
            wx.ListCtrl.__init__(self, parent, id, pos, size, style=style)
            ListCtrlAutoWidthMixin.__init__(self)

    # --Class-------------------------------------------------------------------
    mainMenu = None
    itemMenu = None

    # --Instance ---------------------------------------------------------------
    def __init__(self, parent, data, icons=None, mainMenu=None, itemMenu=None,
        details=None, id=-1, style=(wx.LC_REPORT | wx.LC_SINGLE_SEL)):
        wx.Panel.__init__(self, parent, id, style=wx.WANTS_CHARS)
        # --Data
        if icons == None:
            icons = {}
        self.data = data
        self.icons = icons  # --Default to balt image collection.
        self.mainMenu = mainMenu or self.__class__.mainMenu
        self.itemMenu = itemMenu or self.__class__.itemMenu
        self.details = details
        # --Item/Id mapping
        self.nextItemId = 1
        self.item_itemId = {}
        self.itemId_item = {}
        # --Layout
        sizer = vSizer()
        self.SetSizer(sizer)
        self.SetSizeHints(50, 50)
        # --ListCtrl
        self.gList = gList = Tank.ListCtrl(self, -1, style=style)
        if self.icons:
            gList.SetImageList(icons.GetImageList(), wx.IMAGE_LIST_SMALL)
        # --State info
        self.mouseItem = None
        self.mouseTexts = {}
        self.mouseTextPrev = ''
        # --Columns
        self.UpdateColumns()
        # --Items
        self.sortDirty = False
        self.UpdateItems()
        # --Events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # --Events: Items
        gList.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        gList.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.DoItemMenu)
        gList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        gList.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnStartLabelEdit)
        # --Events: Columns
        gList.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick)
        gList.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.DoColumnMenu)
        gList.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColumnResize)
        # --Mouse movement
        gList.Bind(wx.EVT_MOTION, self.OnMouse)
        gList.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouse)
        gList.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
        # --ScrollPos
        gList.ScrollLines(data.getParam('vScrollPos', 0))
        data.setParam('vScrollPos', gList.GetScrollPos(wx.VERTICAL))
        # --Hack: Default text item background color
        self.defaultTextBackground = wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW)

    # --Item/Id/Index Translation ----------------------------------------------
    def GetItem(self, index):
        """Returns item for specified list index."""
        return self.itemId_item[self.gList.GetItemData(index)]

    def GetId(self, item):
        """Returns id for specified item, creating id if necessary."""
        id = self.item_itemId.get(item)
        if id:
            return id
        # --Else get a new item id.
        id = self.nextItemId
        self.nextItemId += 1
        self.item_itemId[item] = id
        self.itemId_item[id] = item
        return id

    def GetIndex(self, item):
        """Returns index for specified item."""
        return self.gList.FindItemData(-1, self.GetId(item))

    def UpdateIds(self):
        """Updates item/id mappings to account for removed items."""
        removed = set(self.item_itemId.keys()) - set(self.data.keys())
        for item in removed:
            itemId = self.item_itemId[item]
            del self.item_itemId[item]
            del self.itemId_item[itemId]

    # --Updating/Sorting/Refresh -----------------------------------------------
    def UpdateColumns(self):
        """Create/name columns in ListCtrl."""
        data = self.data
        columns = data.getParam('columns', data.tankColumns[:])
        col_name = data.getParam('colNames', {})
        col_width = data.getParam('colWidths', {})
        col_align = data.getParam('colAligns', {})
        for index, column in enumerate(columns):
            name = col_name.get(column, _(column))
            width = col_width.get(column, 30)
            align = wxListAligns[col_align.get(column, 'LEFT')]
            self.gList.InsertColumn(index, name, align)
            self.gList.SetColumnWidth(index, width)

    def UpdateItem(self, index, item=None, selected=tuple()):
        """Populate Item for specified item."""
        if index < 0:
            return
        data, gList = self.data, self.gList
        item = item or self.GetItem(index)
        for iColumn, column in enumerate(data.getColumns(item)):
            gList.SetStringItem(index, iColumn, column)
        gItem = gList.GetItem(index)
        iconKey, textKey, backKey = data.getGuiKeys(item)
        if iconKey and self.icons:
            gItem.SetImage(self.icons[iconKey])
        if textKey:
            gItem.SetTextColour(colors[textKey])
        else:
            gItem.SetTextColour(gList.GetTextColour())
        if backKey:
            gItem.SetBackgroundColour(colors[backKey])
        else:
            gItem.SetBackgroundColour(self.defaultTextBackground)
        gItem.SetState((0, wx.LIST_STATE_SELECTED)[item in selected])
        gItem.SetData(self.GetId(item))
        gList.SetItem(gItem)

    def UpdateItems(self, selected='SAME'):
        """Update all items."""
        gList = self.gList
        items = set(self.data.keys())
        index = 0
        # --Items to select afterwards. (Defaults to current selection.)
        if selected == 'SAME':
            selected = set(self.GetSelected())
        # --Update existing items.
        while index < gList.GetItemCount():
            item = self.GetItem(index)
            if item not in items:
                gList.DeleteItem(index)
            else:
                self.UpdateItem(index, item, selected)
                items.remove(item)
                index += 1
        # --Add remaining new items
        for item in items:
            gList.InsertStringItem(index, '')
            self.UpdateItem(index, item, selected)
            index += 1
        # --Cleanup
        self.UpdateIds()
        self.SortItems()
        self.mouseTexts.clear()

    def SortItems(self, column=None, reverse='CURRENT'):
        """Sort items. Real work is done by data object, and that completed
        sort is then "cloned" list through an intermediate cmp function.

        column: column to sort. Defaults to current sort column.

        reverse:
        * True: Reverse order
        * False: Normal order
        * 'CURRENT': Same as current order for column.
        * 'INVERT': Invert if column is same as current sort column.
        """
        # --Parse column and reverse arguments.
        data = self.data
        if self.sortDirty:
            self.sortDirty = False
            (column, reverse) = (None, 'CURRENT')
        curColumn = data.defaultParam('colSort', data.tankColumns[0])
        column = column or curColumn
        curReverse = data.defaultParam('colReverse', {}).get(column, False)
        if reverse == 'INVERT' and column == curColumn:
            reverse = not curReverse
        elif reverse in ('INVERT', 'CURRENT'):
            reverse = curReverse
        data.updateParam('colReverse')[column] = reverse
        data.setParam('colSort', column)
        # --Sort
        items = self.data.getSorted(column, reverse)
        sortDict = dict((self.item_itemId[y], x) for x, y in enumerate(items))
        self.gList.SortItems(lambda x, y: cmp(sortDict[x], sortDict[y]))
        # --Done
        self.mouseTexts.clear()

    def RefreshData(self):
        """Refreshes underlying data."""
        self.data.refresh()

    def RefreshReport(self):
        """(Optionally) Shows a report of changes after a data refresh."""
        report = self.data.getRefreshReport()
        if report:
            showInfo(self, report, self.data.title)

    def RefreshUI(self, items='ALL', details='SAME'):
        """Refreshes UI for specified file."""
        selected = self.GetSelected()
        if details == 'SAME':
            details = self.GetDetailsItem()
        elif details:
            selected = tuple(details)
        if items == 'ALL':
            self.UpdateItems(selected=selected)
        elif items in self.data:
            self.UpdateItem(self.GetIndex(items), items, selected=selected)
        else:  # --Iterable
            for index in range(self.gList.GetItemCount()):
                if self.GetItem(index) in set(items):
                    self.UpdateItem(index, None, selected=selected)
        self.RefreshDetails(details)

    # --Details view (if it exists)
    def GetDetailsItem(self):
        """Returns item currently being shown in details view."""
        if self.details:
            return self.details.GetDetailsItem()
        return None

    def RefreshDetails(self, item=None):
        """Refreshes detail view associated with data from item."""
        if self.details:
            return self.details.RefreshDetails(item)
        item = item or self.GetDetailsItem()
        if item not in self.data:
            item = None

    # --Selected items
    def GetSelected(self):
        """Return list of items selected (hilighted) in the interface."""
        gList = self.gList
        return [self.GetItem(x) for x in range(gList.GetItemCount())
            if gList.GetItemState(x, wx.LIST_STATE_SELECTED)]

    def ClearSelected(self):
        """Unselect all items."""
        gList = self.gList
        for index in range(gList.GetItemCount()):
            if gList.GetItemState(index, wx.LIST_STATE_SELECTED):
                gList.SetItemState(index, 0, wx.LIST_STATE_SELECTED)

    # --Event Handlers -------------------------------------
    def OnMouse(self, event):
        """Check mouse motion to detect right click event."""
        if event.Moving():
            (mouseItem, mouseHitFlag) = self.gList.HitTest(event.GetPosition())
            if mouseItem != self.mouseItem:
                self.mouseItem = mouseItem
                self.MouseOverItem(mouseItem)
        elif event.Leaving() and self.mouseItem != None:
            self.mouseItem = None
            self.MouseOverItem(None)
        event.Skip()

    def MouseOverItem(self, item):
        """Handle mouse over item by showing tip or similar."""
        pass

    def OnItemSelected(self, event):
        """Item Selected: Refresh details."""
        self.RefreshDetails(self.GetItem(event.m_itemIndex))

    def OnStartLabelEdit(self, event):
        """ We don't supported renaming labels, so don't let anyone start """
        event.Veto()

    def OnSize(self, event):
        """Panel size was changed. Change gList size to match."""
        size = self.GetClientSizeTuple()
        self.gList.SetSize(size)

    def OnScroll(self, event):
        """Event: List was scrolled. Save so can be accessed later."""
        if event.GetOrientation() == wx.VERTICAL:
            self.data.setParam('vScrollPos', event.GetPosition())
        event.Skip()

    def OnColumnResize(self, event):
        """Column resized. Save column size info."""
        iColumn = event.GetColumn()
        column = self.data.getParam('columns')[iColumn]
        self.data.updateParam('colWidths')[column] = self.gList.GetColumnWidth(
            iColumn)

    def OnLeftDown(self, event):
        """Left mouse button was pressed."""
        # self.hitTest = self.gList.HitTest((event.GetX(),event.GetY()))
        event.Skip()

    def OnColumnClick(self, event):
        """Column header was left clicked on. Sort on that column."""
        columns = self.data.getParam('columns')
        self.SortItems(columns[event.GetColumn()], 'INVERT')

    def DoColumnMenu(self, event):
        """Show column menu."""
        if not self.mainMenu:
            return
        iColumn = event.GetColumn()
        menu = wx.Menu()
        for item in self.mainMenu:
            item.AppendToMenu(menu, self, iColumn)
        self.PopupMenu(menu)
        menu.Destroy()

    def DoItemMenu(self, event):
        """Show item menu."""
        if not self.itemMenu:
            return
        selected = self.GetSelected()
        if not selected:
            return
        menu = wx.Menu()
        for item in self.itemMenu:
            item.AppendToMenu(menu, self, selected)
        self.PopupMenu(menu)
        menu.Destroy()

    # --Standard data commands -------------------------------------------------
    def DeleteSelected(self):
        """Deletes selected items."""
        items = self.GetSelected()
        if not items:
            return
        message = _(u'Delete these items? This operation cannot be undone.')
        message += u'\n* ' + u'\n* '.join([self.data.getName(x) for x in items])
        if not askYes(self, message, _(u'Delete Items')):
            return
        for item in items:
            del self.data[item]
        self.RefreshUI()
        self.data.setChanged()


# Links -----------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Links(list):
    """List of menu or button links."""

    class LinksPoint:
        """Point in a link list. For inserting, removing, appending items."""

        def __init__(self, list, index):
            self._list = list
            self._index = index

        def remove(self):
            del self._list[self._index]

        def replace(self, item):
            self._list[self._index] = item

        def insert(self, item):
            self._list.insert(self._index, item)
            self._index += 1

        def append(self, item):
            self._list.insert(self._index + 1, item)
            self._index += 1

    # --Access functions:
    def getClassPoint(self, classObj):
        """Returns index"""
        for index, item in enumerate(self):
            if isinstance(item, classObj):
                return Links.LinksPoint(self, index)
        else:
            return None


# ------------------------------------------------------------------------------
class Link:
    """Link is a command to be encapsulated in a graphic element (menu item, button, etc.)"""

    def __init__(self):
        self.id = None

    def AppendToMenu(self, menu, window, data):
        """Append self to menu as menu item."""
        if isinstance(window, Tank):
            self.gTank = window
            self.selected = window.GetSelected()
            self.data = window.data
            self.title = window.data.title
        else:
            self.window = window
            self.data = data
        # --Generate self.id if necessary (i.e. usually)
        if not self.id:
            self.id = wx.NewId()
        wx.EVT_MENU(window, self.id, self.Execute)

    def Execute(self, event):
        """Event: link execution."""
        raise exception.AbstractError


# ------------------------------------------------------------------------------
class SeparatorLink(Link):
    """Link that acts as a separator item in menus."""

    def AppendToMenu(self, menu, window, data):
        """Add separator to menu."""
        menu.AppendSeparator()


# ------------------------------------------------------------------------------
class MenuLink(Link):
    """Defines a submenu. Generally used for submenus of large menus."""

    def __init__(self, name, oneDatumOnly=False):
        """Initialize. Submenu items should append to self.links."""
        Link.__init__(self)
        self.name = name
        self.links = Links()
        self.oneDatumOnly = oneDatumOnly

    def AppendToMenu(self, menu, window, data):
        """Add self as submenu (along with submenu items) to menu."""
        subMenu = wx.Menu()
        for link in self.links:
            link.AppendToMenu(subMenu, window, data)
        menu.AppendMenu(-1, self.name, subMenu)
        if self.oneDatumOnly and len(data) != 1:
            id = menu.FindItem(self.name)
            menu.Enable(id, False)


# Tanks Links -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class Tanks_Open(Link):
    """Opens data directory in explorer."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _(u'Open...'))
        menu.AppendItem(menuItem)

    def Execute(self, event):
        """Handle selection."""
        dir = self.data.dir
        dir.makedirs()
        dir.start()


# Tank Links ------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Tank_Delete(Link):
    """Deletes selected file from tank."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menu.AppendItem(wx.MenuItem(menu, self.id, _(u'Delete')))

    def Execute(self, event):
        try:
            wx.BeginBusyCursor()
            self.gTank.DeleteSelected()
        finally:
            wx.EndBusyCursor()


# ------------------------------------------------------------------------------
class Tank_Open(Link):
    """Open selected file(s)."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _(u'Open...'))
        menu.AppendItem(menuItem)
        menuItem.Enable(bool(self.selected))

    def Execute(self, event):
        """Handle selection."""
        dir = self.data.dir
        for file in self.selected:
            dir.join(file).start()


# ------------------------------------------------------------------------------
class Tank_Duplicate(Link):
    """Create a duplicate of a tank item, assuming that tank item is a file,
    and using a SaveAs dialog."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _(u'Duplicate...'))
        menu.AppendItem(menuItem)
        menuItem.Enable(len(self.selected) == 1)

    def Execute(self, event):
        srcDir = self.data.dir
        srcName = self.selected[0]
        (root, ext) = srcName.rootExt
        (destDir, destName, wildcard) = (srcDir, root + u' Copy' + ext, u'*' + ext)
        destPath = askSave(self.gTank, _(u'Duplicate as:'), destDir, destName, wildcard)
        if not destPath:
            return
        destDir, destName = destPath.headTail
        if (destDir == srcDir) and (destName == srcName):
            showError(self.window, _(u"Files cannot be duplicated to themselves!"))
            return
        self.data.copy(srcName, destName, destDir)
        if destDir == srcDir:
            self.gTank.RefreshUI()
