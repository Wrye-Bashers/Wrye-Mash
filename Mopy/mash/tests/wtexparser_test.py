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
import unittest

from ..wtexparser import *

class TestHtml(unittest.TestCase):
    def testGenerate(self):
        wtex = "= The Name \n* Some Text"
        p = Parser()
        p.parseString(wtex)
        html = getHtmlFromHeadings(p.getHeading("The Name"))
        expected = ( '<p><a name="TheName"></a>'
                   + '<strong>The Name</strong><br>'
                   + 'Some Text<br></p>')
        self.assertEqual(expected, html)


class TestParser(unittest.TestCase):
    def test_parseSimpleHeading(self):
        wtex = "= The Name "
        p = Parser()
        p.parseString(wtex)
        self.assertNotEqual(None, p.getHeading("The Name"))

    def test_parseSubHeading(self):
        wtex = "= The Name\n== Sub "
        p = Parser()
        p.parseString(wtex)
        self.assertNotEqual(None, p.getHeading("Sub"))
        self.assertEqual("The Name", p.getHeading("Sub").parent.title)
        self.assertEqual(2, p.getHeading("Sub").level)

    def test_parseSimpleText(self):
        wtex = "= The Name \nSome Text"
        p = Parser()
        p.parseString(wtex)
        firstLine = p.getHeading("The Name").getTextLines().next().rawText()
        self.assertEquals("Some Text", firstLine)

    def test_parseSimpleTextWithAstrix(self):
        wtex = "= The Name \n* Some Text"
        p = Parser()
        p.parseString(wtex)
        firstLine = p.getHeading("The Name").getTextLines().next().rawText()
        self.assertEquals("Some Text", firstLine)

    def test_parseSubText(self):
        wtex = "= The Name \n* Some Text\n * Sub"
        p = Parser()
        p.parseString(wtex)
        g = p.getHeading("The Name").getTextLines()
        g.next()
        sndNode = g.next()
        self.assertEquals(2, sndNode.level)
        sndLine = sndNode.rawText()
        self.assertEquals("Sub", sndLine)

    def test_parseSeveralHeadings(self):
        wtex = "=Main1\n==Sub1\n=Main2"
        p = Parser()
        p.parseString(wtex)
        self.assertEquals(1, p.getHeading("Main1").level)
        self.assertEquals(1, p.getHeading("Main2").level)

    def textHelper(self, inText, bold, italic, text):
        result = Parser().parseText(inText)[0]
        self.assertEquals(text, result.text)
        self.assertEquals(italic, result.italic)
        self.assertEquals(bold, result.bold)

    def test_parseText(self):
        self.textHelper('__Text__', True, False, 'Text')
        self.textHelper('~~Text~~', False, True, 'Text')
        self.textHelper('**Text**', True, True, 'Text')

    def test_parseTextEx(self):
        inText = 'Hello **World**'
        result = Parser().parseText(inText)
        self.assertEquals(2, len(result))

    def test_parseLink(self):
        inText = '[[a|b]]'
        result = Parser().parseText(inText)[0]
        self.assertEquals('b', result.text)
        self.assertEquals('a', result.href)

        inText = '[[#|Test]]'
        result = Parser().parseText(inText)[0]
        self.assertEquals('Test', result.text)
        self.assertEquals('#Test', result.href)

        inText = '[[Href]]'
        result = Parser().parseText(inText)[0]
        self.assertEquals('Href', result.text)
        self.assertEquals('Href', result.href)
