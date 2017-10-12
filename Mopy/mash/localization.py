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
import locale
import time
import os
import re
import cPickle
import chardet

reTrans = re.compile(ur'^([ :=\.]*)(.+?)([ :=\.]*$)', re.U)

# Encoding/decoding-------------------------------------------------------------
# --decode unicode strings
#  This is only useful when reading fields from mods, as the encoding is not
#  known.  For normal filesystem interaction, these functions are not needed
encodingOrder = (
    'ascii',  # Plain old ASCII (0-127)
    'gbk',  # GBK (simplified Chinese + some)
    'cp932',  # Japanese
    'cp949',  # Korean
    'cp1252',  # English (extended ASCII)
    'utf8',
    'cp500',
    'UTF-16LE',
)
if os.name == u'nt':
    encodingOrder += ('mbcs',)

_encodingSwap = {
    # The encoding detector reports back some encodings that
    # are subsets of others.  Use the better encoding when
    # given the option
    # 'reported encoding':'actual encoding to use',
    'GB2312'      : 'gbk',  # Simplified Chinese
    'SHIFT_JIS'   : 'cp932',  # Japanese
    'windows-1252': 'cp1252',
    'windows-1251': 'cp1251',
    'utf-8'       : 'utf8',
}


def _getbestencoding(bitstream):
    """Tries to detect the encoding a bitstream was saved in.  Uses Mozilla's
       detection library to find the best match (heuristics)"""
    result = chardet.detect(bitstream)
    encoding_, confidence = result['encoding'], result['confidence']
    encoding_ = _encodingSwap.get(encoding_, encoding_)
    ## Debug: uncomment the following to output stats on encoding detection
    # print
    # print '%s: %s (%s)' % (repr(bitstream),encoding,confidence)
    return encoding_, confidence


def decode(byte_str, encoding=None, avoidEncodings=()):
    if isinstance(byte_str, unicode) or byte_str is None:
        return byte_str
    # Try the user specified encoding first
    if encoding:
        try:
            return unicode(byte_str, encoding)
        except UnicodeDecodeError:
            pass
    # Try to detect the encoding next
    encoding, confidence = _getbestencoding(byte_str)
    if encoding and confidence >= 0.55 and (
                encoding not in avoidEncodings or confidence == 1.0):
        try:
            return unicode(byte_str, encoding)
        except UnicodeDecodeError:
            pass
    # If even that fails, fall back to the old method, trial and error
    for encoding in encodingOrder:
        try:
            return unicode(byte_str, encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError(u'Text could not be decoded using any method')


def encode(text_str, encodings=encodingOrder, firstEncoding=None,
    returnEncoding=False):
    if isinstance(text_str, str) or text_str is None:
        if returnEncoding:
            return text_str, None
        else:
            return text_str
    # Try user specified encoding
    if firstEncoding:
        try:
            text_str = text_str.encode(firstEncoding)
            if returnEncoding:
                return text_str, firstEncoding
            else:
                return text_str
        except UnicodeEncodeError:
            pass
    goodEncoding = None
    # Try the list of encodings in order
    for encoding in encodings:
        try:
            temp = text_str.encode(encoding)
            detectedEncoding = _getbestencoding(temp)
            if detectedEncoding[0] == encoding:
                # This encoding also happens to be detected
                # By the encoding detector as the same thing,
                # which means use it!
                if returnEncoding:
                    return temp, encoding
                else:
                    return temp
            # The encoding detector didn't detect it, but
            # it works, so save it for later
            if not goodEncoding:
                goodEncoding = (temp, encoding)
        except UnicodeEncodeError:
            pass
    # Non of the encodings also where detectable via the
    # detector, so use the first one that encoded without error
    if goodEncoding:
        if returnEncoding:
            return goodEncoding
        else:
            return goodEncoding[0]
    raise UnicodeEncodeError(
        u'Text could not be encoded using any of the following encodings: %s' % encodings)


# Locale: String Translation --------------------------------------------------
def compileTranslator(txtPath, pklPath):
    """Compiles specified txtFile into pklFile."""
    reSource = re.compile(ur'^=== ', re.U)
    reValue = re.compile(ur'^>>>>\s*$', re.U)
    reBlank = re.compile(ur'^\s*$', re.U)
    reNewLine = re.compile(ur'\\n', re.U)
    # --Scan text file
    translator = {}

    def addTranslation(key, value):
        key, value = key[:-1], value[:-1]
        # print `key`, `value`
        if key and value:
            key = reTrans.match(key).group(2)
            value = reTrans.match(value).group(2)
            translator[key] = value

    key, value, mode = '', '', 0
    textFile = file(txtPath)
    for line in textFile:
        # --Blank line. Terminates key, value pair
        if reBlank.match(line):
            addTranslation(key, value)
            key, value, mode = '', '', 0
        # --Begin key input?
        elif reSource.match(line):
            addTranslation(key, value)
            key, value, mode = '', '', 1
        # --Begin value input?
        elif reValue.match(line):
            mode = 2
        elif mode == 1:
            key += line
        elif mode == 2:
            value += line
    addTranslation(key, value)  # --In case missed last pair
    textFile.close()
    # --Write translator to pickle
    filePath = pklPath
    tempPath = filePath + '.tmp'
    cPickle.dump(translator, open(tempPath, 'w'))
    if os.path.exists(filePath):
        os.remove(filePath)
    os.rename(tempPath, filePath)


def formatInteger(value):
    """Convert integer to string formatted to locale."""
    return decode(locale.format('%d', int(value), True),
        locale.getpreferredencoding())


def formatDate(value):
    """Convert time to string formatted to to locale's default date/time."""
    try:
        local = time.localtime(value)
    except ValueError:  # local time in windows can't handle negative values
        local = time.gmtime(value)
        # deprint(u'Timestamp %d failed to convert to local, using %s' % (
        #     value, local))
    return decode(time.strftime('%c', local), locale.getpreferredencoding())


# --Do translator test and set
currentLocale = locale.getlocale()
if locale.getlocale() == (None, None):
    locale.setlocale(locale.LC_ALL, '')
language = locale.getlocale()[0].split('_', 1)[0]
# if language.lower() == 'german': language = 'de'  # --Hack for German speakers who arne't 'DE'.
# languagePkl, languageTxt = (os.path.join('data', language + ext) for ext in
languagePkl, languageTxt = (os.path.join('locale', language + ext) for ext in ('.pkl', '.txt'))
# --Recompile pkl file?
if os.path.exists(languageTxt) and (not os.path.exists(languagePkl) or (os.path.getmtime(languageTxt) > os.path.getmtime(languagePkl))):
    compileTranslator(languageTxt, languagePkl)
# --Use dictionary from pickle as translator
if os.path.exists(languagePkl):
    pklFile = open(languagePkl)
    reEscQuote = re.compile(ur"\\'", re.U)
    _translator = cPickle.load(pklFile)
    pklFile.close()


    def _(text, encode=True):
        if encode:
            text = reEscQuote.sub("'", text.encode('string_escape'))
        head, core, tail = reTrans.match(text).groups()
        if core and core in _translator:
            text = head + _translator[core] + tail
        if encode:
            text = text.decode('string_escape')
        # return _translator.get(text, text)
        return text
else:
    def _(text, encode=True):
        return text