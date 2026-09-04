# -*- coding: utf-8 -*-
"""loadMap graph integrity: CRLF-tainted node names must not poison world.nodes."""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON = os.path.join(REPO, 'script', 'global', 'nobitaxd', 'vdk', 'simcity',
                      'libs', 'common.lua')
DATA = os.path.join(REPO, 'script', 'global', 'nobitaxd', 'vdk', 'simcity',
                    'libs', 'data.lua')


class TestNodeCoordSanitization(unittest.TestCase):
    def test_trim_helper_exists(self):
        src = open(COMMON, 'rb').read()
        self.assertIn(b'function SimCityTrimCell(', src)
        self.assertIn(b'function nodeNameToCoords(', src)

    def test_nodename_requires_two_numeric_parts(self):
        src = open(COMMON, 'rb').read().decode('latin-1')
        # Contract: reject ~= 2 parts after split on _
        self.assertIn('getn(point) ~= 2', src)
        self.assertIn('SimCityTrimCell(point[1])', src)

    def test_loadmap_never_links_with_raw_dx_on_maybe_nil_x(self):
        src = open(DATA, 'rb').read()
        # The live crash was: otherNode.x - world.nodes[testNode].x
        self.assertNotIn(b'local dx = otherNode.x - world.nodes[testNode].x', src)
        self.assertIn(b'never insert a node without numeric x,y', src)

    def test_tabfile_readers_trim_cells(self):
        src = open(COMMON, 'rb').read()
        self.assertGreaterEqual(src.count(b'SimCityTrimCell('), 4)


if __name__ == '__main__':
    unittest.main()
