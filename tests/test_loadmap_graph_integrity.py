# -*- coding: utf-8 -*-
"""loadMap / node coord integrity contracts for Kingsoft Lua 4.0."""
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON = os.path.join(REPO, 'script', 'global', 'nobitaxd', 'vdk', 'simcity',
                      'libs', 'common.lua')
DATA = os.path.join(REPO, 'script', 'global', 'nobitaxd', 'vdk', 'simcity',
                    'libs', 'data.lua')
STRING_LIB = os.path.join(REPO, 'script', 'lib', 'string.lua')


class TestSplitNotBroken(unittest.TestCase):
    def test_no_custom_split_with_plain_flag(self):
        src = open(COMMON, 'rb').read()
        # The 4th plain=1 arg breaks Kingsoft Lua 4.0 strfind and drops all x_y nodes.
        self.assertNotIn(b'strfind(szFullString, szSeparator, nFindStartIndex, 1)', src)
        self.assertNotIn(b'function split(szFullString', src)

    def test_engine_string_split_exists(self):
        src = open(STRING_LIB, 'rb').read()
        self.assertIn(b'function split(str,splitor)', src)
        # engine split must NOT use 4-arg plain strfind
        self.assertNotIn(b'strfind(str,splitor,strStart, 1)', src)
        self.assertNotIn(b'strfind(str,splitor,strStart,1)', src)


class TestLoadMapGuards(unittest.TestCase):
    def test_no_drop_spam_print(self):
        src = open(DATA, 'rb').read()
        self.assertNotIn(b'drop invalid preset node', src)

    def test_refuses_nil_coord_insert(self):
        src = open(DATA, 'rb').read()
        self.assertIn(b'x ~= nil and y ~= nil', src)

    def test_trim_helper_present(self):
        src = open(COMMON, 'rb').read()
        self.assertIn(b'function SimCityTrimCell(', src)
        self.assertIn(b'function nodeNameToCoords(', src)

    def test_nodename_uses_simple_split_tonumber(self):
        src = open(COMMON, 'rb').read().decode('latin-1')
        self.assertIn('local point = split(nodeName, "_")', src)
        self.assertIn('tonumber(point[1])', src)
        self.assertIn('tonumber(point[2])', src)
        self.assertNotIn('getn(point) ~= 2', src)


if __name__ == '__main__':
    unittest.main()
