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
# --Imports
import re
import string
import sys
import types


# --Callables Class
class Callables:
    # --Ctor
    def __init__(self):
        self.callObjs = {}
        self.callHelp = {}

    # --Add a callable
    def add(self, callKey, callObj, callHelp=''):
        self.callObjs[callKey] = callObj
        self.callHelp[callKey] = callHelp

    # --Help
    def help(self, callKey):
        raise "Undefined."

    # --List
    def list(self):
        for key in self.callObjs.keys():
            # print ' ', key, sel
            print ' ', key, self
        raise "Undefined."

    # --Main
    def main(self):
        callObjs = self.callObjs
        # --Call key, tail
        callParts = string.split(sys.argv[1], '.', 1)
        callKey = callParts[0]
        callTail = (len(callParts) > 1 and callParts[1])
        # --Help request?
        if callKey == '-h':
            self.help()
            sys.exit(0)
        # --Not have key?
        if not callObjs.has_key(callKey):
            print "Unknown function/object:", callKey
            return
        # --Callable
        callObj = callObjs[callKey]
        if type(callObj) == types.StringType:
            callObj = eval(callObj)
        if callTail:
            callObj = eval('callObj.' + callTail)
        # --Args
        args = sys.argv[2:]
        # --Keywords?
        keywords = {}
        argDex = 0
        reKeyArg = re.compile(r'^\-(\D\w+)')
        reKeyBool = re.compile(r'^\+(\D\w+)')
        while argDex < len(args):
            arg = args[argDex]
            if reKeyArg.match(arg):
                keyword = reKeyArg.match(arg).group(1)
                value = args[argDex + 1]
                keywords[keyword] = value
                del args[argDex:argDex + 2]
            elif reKeyBool.match(arg):
                keyword = reKeyBool.match(arg).group(1)
                keywords[keyword] = 1
                del args[argDex]
            else:
                argDex = argDex + 1
        # --Apply
        apply(callObj, args, keywords)


# --Callables Singleton
callables = Callables()
