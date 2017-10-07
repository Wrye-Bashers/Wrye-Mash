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

reTrans = re.compile(r'^([ :=\.]*)(.+?)([ :=\.]*$)')

# Locale: String Translation --------------------------------------------------
def compileTranslator(txtPath, pklPath):
    """Compiles specified txtFile into pklFile."""
    reSource = re.compile(r'^=== ')
    reValue = re.compile(r'^>>>>\s*$')
    reBlank = re.compile(r'^\s*$')
    reNewLine = re.compile(r'\\n')
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
    return locale.format('%d', int(value), 1)


def formatDate(value):
    """Convert time to string formatted to to locale's default date/time."""
    return time.strftime('%c', time.localtime(value))

# --Do translator test and set
currentLocale = locale.getlocale()
if locale.getlocale() == (None, None):
    locale.setlocale(locale.LC_ALL, '')
language = locale.getlocale()[0].split('_', 1)[0]
#if language.lower() == 'german': language = 'de'  # --Hack for German speakers who arne't 'DE'.
#languagePkl, languageTxt = (os.path.join('data', language + ext) for ext in
languagePkl, languageTxt = (os.path.join('locale', language + ext) for ext in
('.pkl', '.txt'))
# --Recompile pkl file?
if os.path.exists(languageTxt) and (
        not os.path.exists(languagePkl) or (
            os.path.getmtime(languageTxt) > os.path.getmtime(languagePkl)
    )
):
    compileTranslator(languageTxt, languagePkl)
# --Use dictionary from pickle as translator
if os.path.exists(languagePkl):
    pklFile = open(languagePkl)
    reEscQuote = re.compile(r"\\'")
    _translator = cPickle.load(pklFile)
    pklFile.close()


    def _(text, encode=True):
        if encode: text = reEscQuote.sub("'", text.encode('string_escape'))
        head, core, tail = reTrans.match(text).groups()
        if core and core in _translator:
            text = head + _translator[core] + tail
        if encode: text = text.decode('string_escape')
        # return _translator.get(text, text)
        return text
else:
    def _(text, encode=True):
        return text
