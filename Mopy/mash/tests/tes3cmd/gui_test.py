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
import os

from ...tes3cmd import gui

class TestCleaner(unittest.TestCase):
    def getOutput(self, fn):
        c = gui.OutputParserMixin()
        fn = os.path.join(os.path.dirname(__file__), fn)
        return c.ParseOutput(open(fn).read()) 

    def testParse1(self):
        stats, output = self.getOutput('output.imclean.txt')

        expectedStats = ( 'duplicate object instance:     3\n'
                        + 'duplicate record:     2\n'
                        + 'redundant CELL.AMBI:     1\n'
                        + 'redundant CELL.WHGT:     2\n')

        expectedOutput = ( 'Cleaned duplicate record (BOOK): chargen statssheet\n'
                         + 'Cleaned duplicate record (DOOR): chargen exit door\n'
                         + 'Cleaned duplicate object instance (CharGen_cabindoor FRMR: 6034) from CELL: bitter coast region (-1, -9)\n'
                         + 'Cleaned duplicate object instance (Imperial Guard FRMR: 63431) from CELL: seyda neen (-2, -9)\n'
                         + 'Cleaned duplicate object instance (flora_bc_tree_02 FRMR: 24458) from CELL: seyda neen (-2, -9)\n'
                         + 'Cleaned redundant WHGT from CELL: imperial prison ship\n'
                         + 'Cleaned redundant AMBI,WHGT from CELL: seyda neen, census and excise office\n')
        self.assertEqual(stats, expectedStats)
        self.assertEqual(output, expectedOutput)

    def testParse2(self):
        stats, output = self.getOutput('output.tribclean.txt')
        
        expectedStats = ( 'Evil-GMST Bloodmoon:    61\n'
                        + 'Evil-GMST Tribunal:     5\n'
                        + 'duplicate record:  1479\n'
                        + 'junk-CELL:    14\n'
                        + 'redundant CELL.AMBI:     7\n'
                        + 'redundant CELL.WHGT:     7\n')

        self.assertEqual(stats, expectedStats)
        self.assertEqual(output, '')

    def testParse3(self):
        stats, output = self.getOutput('output.notmodified.txt')

        self.assertEqual(stats, 'Not modified')
        self.assertEqual(output, '')
